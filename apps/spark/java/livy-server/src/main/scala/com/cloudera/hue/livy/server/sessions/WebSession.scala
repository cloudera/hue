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

package com.cloudera.hue.livy.server.sessions

import java.net.URL
import java.util.concurrent.TimeUnit

import com.cloudera.hue.livy._
import com.cloudera.hue.livy.msgs.ExecuteRequest
import com.cloudera.hue.livy.sessions._
import dispatch._
import org.json4s.jackson.Serialization.write
import org.json4s.{DefaultFormats, Formats}

import scala.collection.mutable.ArrayBuffer
import scala.concurrent.duration.Duration
import scala.concurrent.{Future, _}

class WebSession(val id: Int,
                 val kind: Kind,
                 val proxyUser: Option[String]) extends Session with Logging {

  protected implicit def executor: ExecutionContextExecutor = ExecutionContext.global
  protected implicit def jsonFormats: Formats = DefaultFormats

  protected[this] var _state: State = Starting()

  private[this] var _lastActivity = Long.MaxValue
  private[this] var _url: Option[URL] = None

  private[this] var _executedStatements = 0
  private[this] var _statements = IndexedSeq[Statement]()

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

  override def lastActivity: Long = _lastActivity

  override def state: State = _state

  override def executeStatement(content: ExecuteRequest): Statement = {
    ensureIdle {
      _state = Busy()
      touchLastActivity()

      var req = (svc / "execute").setContentType("application/json", "UTF-8")
      req = req << write(content)

      val future = Http(req OK as.json4s.Json).map { case (resp) =>
        synchronized {
          transition(Idle())
          resp
        }
      }

      var statement = new Statement(_executedStatements, content, future)

      _executedStatements += 1
      _statements = _statements :+ statement

      statement
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
        case Busy() =>
          Future {
            waitForStateChange(Busy(), Duration(10, TimeUnit.SECONDS))
            stop()
          }
        case ShuttingDown() =>
          Future {
            waitForStateChange(ShuttingDown(), Duration(10, TimeUnit.SECONDS))
            stop()
          }
        case Error() | Dead() =>
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
