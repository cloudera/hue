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

package com.cloudera.hue.livy.server.interactive

import java.net.URL
import java.util.concurrent.TimeUnit

import com.cloudera.hue.livy._
import com.cloudera.hue.livy.msgs.ExecuteRequest
import com.cloudera.hue.livy.sessions._
import dispatch._
import org.json4s.JsonAST.JNull
import org.json4s.jackson.Serialization.write
import org.json4s.{DefaultFormats, Formats, JValue}

import scala.annotation.tailrec
import scala.concurrent.duration.Duration
import scala.concurrent.{Future, _}

abstract class InteractiveWebSession(val id: Int, createInteractiveRequest: CreateInteractiveRequest) extends InteractiveSession with Logging {

  protected implicit def executor: ExecutionContextExecutor = ExecutionContext.global
  protected implicit def jsonFormats: Formats = DefaultFormats

  protected[this] var _state: State = Starting()

  private[this] var _lastActivity = Long.MaxValue
  private[this] var _url: Option[URL] = None

  private[this] var _executedStatements = 0
  private[this] var _statements = IndexedSeq[Statement]()

  override def kind = createInteractiveRequest.kind

  override def proxyUser = createInteractiveRequest.proxyUser

  override def url: Option[URL] = _url

  override def url_=(url: URL) = {
    ensureState(Starting(), {
      _state = Idle()
      _url = Some(url)
    })
  }

  private def svc = {
    val url = _url.head
    dispatch.url(url.toString)
  }

  override def lastActivity: Option[Long] = Some(_lastActivity)

  override def state: State = _state

  override def executeStatement(content: ExecuteRequest): Statement = {
    ensureIdle {
      _state = Busy()
      touchLastActivity()

      val req = (svc / "execute").setContentType("application/json", "UTF-8") << write(content)

      val future = Http(req OK as.json4s.Json).map { case resp: JValue =>
        resp \ "result" match {
          case JNull =>
            // The result isn't ready yet. Loop until it is.
            val id = (resp \ "id").extract[Int]
            waitForStatement(id)
          case result =>
            transition(Idle())
            result
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

    resp \ "result" match {
      case JNull =>
        Thread.sleep(1000)
        waitForStatement(id)
      case result =>
        transition(Idle())
        result
    }
  }

  override def statements: IndexedSeq[Statement] = _statements

  override def interrupt(): Future[Unit] = {
    stop()
  }

  override def stop(): Future[Unit] = {
    synchronized {
      _state match {
        case Idle() =>
          _state = Busy()

          Http(svc.DELETE OK as.String).map { case rep =>
            synchronized {
              _state = Dead()
            }

            Unit
          }
        case NotStarted() =>
          Future {
            waitForStateChange(NotStarted(), Duration(10, TimeUnit.SECONDS))
            stop()
          }
        case Starting() =>
          Future {
            waitForStateChange(Starting(), Duration(10, TimeUnit.SECONDS))
            stop()
          }
        case Busy() | Running() =>
          Future {
            waitForStateChange(Busy(), Duration(10, TimeUnit.SECONDS))
            stop()
          }
        case ShuttingDown() =>
          Future {
            waitForStateChange(ShuttingDown(), Duration(10, TimeUnit.SECONDS))
            stop()
          }
        case Error() | Dead() | Success() =>
          Future.successful(Unit)
      }
    }
  }

  private def transition(state: State) = synchronized {
    _state = state
  }

  private def touchLastActivity() = {
    _lastActivity = System.currentTimeMillis()
  }

  private def ensureState[A](state: State, f: => A) = {
    synchronized {
      if (_state == state) {
        f
      } else {
        throw new IllegalStateException("Session is in state %s" format _state)
      }
    }
  }

  private def ensureIdle[A](f: => A) = {
    ensureState(Idle(), f)
  }

  private def ensureRunning[A](f: => A) = {
    synchronized {
      _state match {
        case Idle() | Busy() =>
          f
        case _ =>
          throw new IllegalStateException("Session is in state %s" format _state)
      }
    }
  }
}
