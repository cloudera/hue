package com.cloudera.hue.livy.server.sessions

import java.net.URL

import com.cloudera.hue.livy._
import com.cloudera.hue.livy.msgs.ExecuteRequest
import com.cloudera.hue.livy.server.Statement
import com.cloudera.hue.livy.server.sessions.Session._
import dispatch._
import org.json4s.jackson.Serialization.write
import org.json4s.{DefaultFormats, Formats}

import scala.annotation.tailrec
import scala.collection.mutable.ArrayBuffer
import scala.concurrent.{Future, _}

class WebSession(val id: String) extends Session with Logging {

  protected implicit def executor: ExecutionContextExecutor = ExecutionContext.global
  protected implicit def jsonFormats: Formats = DefaultFormats

  protected[this] var _state: State = Starting()

  private[this] var _lastActivity = Long.MaxValue
  private[this] var _url: Option[URL] = None

  private[this] var executedStatements = 0
  private[this] var statements_ = new ArrayBuffer[Statement]

  override def url: Option[URL] = _url

  override def url_=(url: URL) = {
    ensureState(Session.Starting(), {
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

      var statement = new Statement(executedStatements, content, future)

      executedStatements += 1
      statements_ += statement

      statement
    }
  }

  override def statement(statementId: Int): Option[Statement] = statements_.lift(statementId)

  override def statements(): Seq[Statement] = statements_.toSeq

  override def statements(fromIndex: Integer, toIndex: Integer): Seq[Statement] = {
    statements_.slice(fromIndex, toIndex).toSeq
  }

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
            waitForStateChange(NotStarted(), { stop() })
          }
        case Starting() =>
          Future {
            waitForStateChange(Starting(), { stop() })
          }
        case Busy() =>
          Future {
            waitForStateChange(Busy(), { stop() })
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
