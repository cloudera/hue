package com.cloudera.hue.livy.server.sessions

import com.cloudera.hue.livy._
import dispatch._
import org.json4s.jackson.Serialization.write
import org.json4s.{DefaultFormats, Formats}

import scala.annotation.tailrec
import scala.concurrent.{Future, _}

abstract class SparkWebSession(val id: String, hostname: String, port: Int) extends Session with Logging {

  protected implicit def executor: ExecutionContextExecutor = ExecutionContext.global
  protected implicit def jsonFormats: Formats = DefaultFormats

  private[this] var _lastActivity = Long.MaxValue
  private[this] var _state: State = Idle()
  private[this] val svc = host(hostname, port)

  override def lastActivity: Long = _lastActivity

  override def state: State = _state

  override def executeStatement(statement: String): Future[ExecuteResponse] = {
    ensureIdle {
      _state = Busy()
      touchLastActivity()

      var req = (svc / "statements").setContentType("application/json", "UTF-8")
      req = req << write(ExecuteRequest(statement))

      Http(req OK as.json4s.Json).map {
        transition(Idle())
        _.extract[ExecuteResponse]
      }
    }
  }

  override def statement(statementId: Int): Future[ExecuteResponse] = {
    ensureRunning {
      val req = svc / "statements" / statementId

      for {
        body <- Http(req OK as.json4s.Json)
      } yield body.extract[ExecuteResponse]
    }
  }

  override def statements(): Future[List[ExecuteResponse]] = {
    ensureRunning {
      val req = svc / "statements"

      for {
        body <- Http(req OK as.json4s.Json)
      } yield body.extract[List[ExecuteResponse]]
    }
  }

  override def statements(fromIndex: Integer, toIndex: Integer): Future[List[ExecuteResponse]] = {
    ensureRunning {
      val req = (svc / "statements")
        .addQueryParameter("from", fromIndex.toString)
        .addQueryParameter("to", toIndex.toString)

      for {
        body <- Http(req OK as.json4s.Json)
      } yield body.extract[List[ExecuteResponse]]
    }
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
        case Starting() =>
          Future {
            waitForStateChangeFrom(Starting(), { stop() })
          }
        case Busy() =>
          Future {
            waitForStateChangeFrom(Busy(), { stop() })
          }
        case Dead() =>
          Future.successful(Unit)
      }
    }
  }

  private def transition(state: State) = synchronized {
    _state = state
  }

  @tailrec
  private def waitForStateChangeFrom[A](state: State, f: => A): A = {
    if (_state == state) {
      Thread.sleep(1000)
      waitForStateChangeFrom(state, f)
    } else {
      f
    }
  }

  private def touchLastActivity() = {
    _lastActivity = System.currentTimeMillis()
  }

  private def ensureIdle[A](f: => A) = {
    synchronized {
      if (_state == Idle()) {
        f
      } else {
        throw new IllegalStateException("Session is in state %s" format _state)
      }
    }
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
