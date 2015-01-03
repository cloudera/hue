package com.cloudera.hue.livy.server

import com.cloudera.hue.livy._
import dispatch._
import org.json4s.jackson.Serialization.write
import org.json4s.{DefaultFormats, Formats}

import scala.annotation.tailrec
import scala.concurrent.{Future, _}

abstract class SparkWebSession(val id: String, hostname: String, port: Int)
  extends Session
  with Logging {

  protected implicit def executor: ExecutionContextExecutor = ExecutionContext.global
  protected implicit def jsonFormats: Formats = DefaultFormats

  private[this] var _lastActivity = Long.MaxValue
  private[this] var _state: State = Running()
  private[this] val svc = host(hostname, port)

  override def lastActivity: Long = _lastActivity

  override def state: State = _state

  override def executeStatement(statement: String): Future[ExecuteResponse] = {
    ensureRunning {
      touchLastActivity()

      var req = (svc / "statements").setContentType("application/json", "UTF-8")
      req = req << write(ExecuteRequest(statement))

      for {
        body <- Http(req OK as.json4s.Json)
      } yield body.extract[ExecuteResponse]
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
    close()
  }

  override def close(): Future[Unit] = {
    synchronized {
      _state match {
        case Running() =>
          _state = Stopping()

          Http(svc.DELETE OK as.String).map { case rep =>
            synchronized {
              _state = Stopped()
            }

            Unit
          }
        case Stopping() =>
          @tailrec
          def waitForStateChange(state: State): Unit = {
            if (_state == state) {
              Thread.sleep(1000)
              waitForStateChange(state)
            }
          }

          Future {
            waitForStateChange(Stopping())

            if (_state == Stopped()) {
              Future.successful(Unit)
            } else {
              Future.failed(new IllegalStateException("livy-repl did not stop: %s" format _state))
            }
          }
        case Stopped() =>
          Future.successful(Unit)
      }
    }
  }

  private def touchLastActivity() = {
    _lastActivity = System.currentTimeMillis()
  }

  private def ensureRunning[A](f: => A) = {
    synchronized {
      if (_state == Running()) {
        f
      } else {
        throw new IllegalStateException("Session is in state %s" format _state)
      }
    }
  }
}
