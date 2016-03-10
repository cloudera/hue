/*
 * Licensed to Cloudera, Inc. under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  Cloudera, Inc. licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package com.cloudera.hue.livy.spark.interactive

import java.net.{ConnectException, URL}
import java.util.concurrent.TimeUnit

import com.cloudera.hue.livy._
import com.cloudera.hue.livy.ExecuteRequest
import com.cloudera.hue.livy.sessions._
import com.cloudera.hue.livy.sessions.interactive.{Statement, InteractiveSession}
import com.cloudera.hue.livy.spark.SparkProcess
import dispatch._
import org.json4s.JsonAST.{JNull, JString}
import org.json4s.jackson.Serialization.write
import org.json4s.{DefaultFormats, Formats, JValue}

import scala.annotation.tailrec
import scala.concurrent.duration.Duration
import scala.concurrent.{Future, _}

abstract class InteractiveWebSession(val id: Int,
                                     process: SparkProcess,
                                     request: CreateInteractiveRequest)
  extends InteractiveSession
  with Logging {

  protected implicit def executor: ExecutionContextExecutor = ExecutionContext.global
  protected implicit def jsonFormats: Formats = DefaultFormats

  protected[this] var _state: SessionState = SessionState.Starting()

  private[this] var _lastActivity = Long.MaxValue
  private[this] var _url: Option[URL] = None

  private[this] var _executedStatements = 0
  private[this] var _statements = IndexedSeq[Statement]()

  override def kind = request.kind

  override def logLines() = process.inputLines

  override def proxyUser = request.proxyUser

  override def url: Option[URL] = _url

  override def url_=(url: URL) = {
    ensureState(SessionState.Starting(), {
      _state = SessionState.Idle()
      _url = Some(url)
    })
  }

  private def svc = {
    val url = _url.head
    dispatch.url(url.toString)
  }

  override def lastActivity: Option[Long] = Some(_lastActivity)

  override def state: SessionState = _state

  override def executeStatement(content: ExecuteRequest): Statement = {
    ensureRunning {
      _state = SessionState.Busy()
      touchLastActivity()

      val req = (svc / "execute").setContentType("application/json", "UTF-8") << write(content)

      val future = Http(req OK as.json4s.Json).map { case resp: JValue =>
        parseResponse(resp).getOrElse {
          // The result isn't ready yet. Loop until it is.
          val id = (resp \ "id").extract[Int]
          waitForStatement(id)
        }
      }

      val statement = new Statement(_executedStatements, content, future)

      _executedStatements += 1
      _statements = _statements :+ statement

      statement
    }
  }

  @tailrec
  private def waitForStatement(id: Int): JValue = {
    val req = (svc / "history" / id).setContentType("application/json", "UTF-8")
    val resp = Await.result(Http(req OK as.json4s.Json), Duration.Inf)

    parseResponse(resp) match {
      case Some(result) => result
      case None =>
        Thread.sleep(1000)
        waitForStatement(id)
    }
  }

  private def parseResponse(response: JValue): Option[JValue] = {
    response \ "result" match {
      case JNull => None
      case result =>
        // If the response errored out, it's possible it took down the interpreter. Check if
        // it's still running.
        result \ "status" match {
          case JString("error") =>
            if (replErroredOut()) {
              transition(SessionState.Error())
            } else {
              transition(SessionState.Idle())
            }
          case _ => transition(SessionState.Idle())
        }

        Some(result)
    }
  }

  private def replErroredOut() = {
    val req = svc.setContentType("application/json", "UTF-8")
    val response = Await.result(Http(req OK as.json4s.Json), Duration.Inf)

    response \ "state" match {
      case JString("error") => true
      case _ => false
    }
  }

  override def statements: IndexedSeq[Statement] = _statements

  override def interrupt(): Future[Unit] = {
    stop()
  }

  override def stop(): Future[Unit] = {
    val future: Future[Unit] = synchronized {
      _state match {
        case SessionState.Idle() =>
          _state = SessionState.Busy()

          Http(svc.DELETE OK as.String).either() match {
            case (Right(_) | Left(_: ConnectException)) =>
              // Make sure to eat any connection errors because the repl shut down before it sent
              // out an OK.
              synchronized {
                _state = SessionState.Dead()
              }

              Future.successful(())

            case Left(t: Throwable) =>
              Future.failed(t)
          }
        case SessionState.NotStarted() =>
          Future {
            waitForStateChange(SessionState.NotStarted(), Duration(10, TimeUnit.SECONDS))
            stop()
          }
        case SessionState.Starting() =>
          Future {
            waitForStateChange(SessionState.Starting(), Duration(10, TimeUnit.SECONDS))
            stop()
          }
        case SessionState.Busy() | SessionState.Running() =>
          Future {
            waitForStateChange(SessionState.Busy(), Duration(10, TimeUnit.SECONDS))
            stop()
          }
        case SessionState.ShuttingDown() =>
          Future {
            waitForStateChange(SessionState.ShuttingDown(), Duration(10, TimeUnit.SECONDS))
            stop()
          }
        case SessionState.Error(_) | SessionState.Dead(_) | SessionState.Success(_) =>
          Future.successful(Unit)
      }
    }

    future.andThen { case r =>
      process.waitFor()
      r
    }
  }

  private def transition(state: SessionState) = synchronized {
    _state = state
  }

  private def touchLastActivity() = {
    _lastActivity = System.currentTimeMillis()
  }

  private def ensureState[A](state: SessionState, f: => A) = {
    synchronized {
      if (_state == state) {
        f
      } else {
        throw new IllegalStateException("Session is in state %s" format _state)
      }
    }
  }

  private def ensureRunning[A](f: => A) = {
    synchronized {
      _state match {
        case SessionState.Idle() | SessionState.Busy() =>
          f
        case _ =>
          throw new IllegalStateException("Session is in state %s" format _state)
      }
    }
  }

  // Error out the job if the process errors out.
  Future {
    if (process.waitFor() == 0) {
      // Set the state to done if the session shut down before contacting us.
      _state match {
        case (SessionState.Dead(_) | SessionState.Error(_) | SessionState.Success(_)) =>
        case _ =>
          _state = SessionState.Success()
      }
    } else {
      _state = SessionState.Error()
    }
  }
}
