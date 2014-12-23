package com.cloudera.hue.livy.server

import java.util.concurrent.TimeoutException

import com.cloudera.hue.livy.{ExecuteRequest, ExecuteResponse, Logging}
import dispatch._
import org.json4s.JsonDSL._
import org.json4s._
import org.json4s.jackson.JsonMethods._
import org.json4s.jackson.Serialization.write

import scala.annotation.tailrec
import scala.concurrent.duration._
import scala.concurrent.{Await, Future}
import scala.io.Source

object SparkProcessSession {
  val LIVY_HOME = System.getenv("LIVY_HOME")
  val SPARK_SHELL = LIVY_HOME + "/spark-shell"

  // Loop until we've started a process with a valid port.
  private def startProcess(): (Process, Int) = {
    val regex = """Starting livy-repl on port (\d+)""".r

    @tailrec
    def parsePort(lines: Iterator[String]): Option[Int] = {
      if (lines.hasNext) {
        val line = lines.next()
        line match {
          case regex(port_) => Some(port_.toInt)
          case _ => parsePort(lines)
        }
      } else {
        None
      }
    }

    def startProcess(): (Process, Int) = {
      val pb = new ProcessBuilder(SPARK_SHELL)
      pb.environment().put("PORT", "0")
      val process = pb.start()

      val source = Source.fromInputStream(process.getInputStream)
      val lines = source.getLines()

      parsePort(lines) match {
        case Some(port) => {
          source.close()
          process.getInputStream.close()
          (process, port)
        }
        case None =>
          // Make sure to reap the process.
          process.waitFor()
          throw new Exception("Couldn't start livy-repl")
      }
    }

    startProcess()
  }
}

class SparkProcessSession(val id: String) extends Session with Logging {

  import com.cloudera.hue.livy.server.SparkProcessSession._

  private[this] var _lastActivity = Long.MaxValue
  private[this] var _state: State = Running()
  private[this] val (process, port) = startProcess()
  private[this] val svc = host("localhost", port)

  override def lastActivity: Long = _lastActivity

  override def state: State = _state

  override def executeStatement(statement: String): Future[ExecuteResponse] = {
    ensureRunning {
      touchLastActivity()

      val req = (svc / "statements")
        .POST
        .setContentType("application/json", "UTF-8")
        .setBody(compact(write(ExecuteRequest(statement))))

      for {
        rep <- Http(req OK as.String)
      } yield parse(rep).extract
    }
  }

  override def statement(statementId: Int): Future[ExecuteResponse] = {
    ensureRunning {
      val req = svc / "statements" / statementId

      for {
        rep <- Http(req OK as.String)
      } yield parse(rep).extract
    }
  }

  override def statements(): Future[List[ExecuteResponse]] = {
    ensureRunning {
      val req = svc / "statements"

      for {
        rep <- Http(req OK as.String)
      } yield parse(rep).extract
    }
  }

  override def statements(fromIndex: Integer, toIndex: Integer): Future[List[ExecuteResponse]] = {
    ensureRunning {
      val req = (svc / "statements")
        .addQueryParameter("from", fromIndex.toString)
        .addQueryParameter("to", toIndex.toString)

      for {
        rep <- Http(req OK as.String)
      } yield parse(rep).extract
    }
  }
    override def interrupt(): Unit = {
    close()
  }

  override def close(): Unit = {
    synchronized {
      _state match {
        case Running() => {
          _state = Stopping()

          // Give the repl some time to shut down cleanly.
          try {
            Await.ready(Http(svc.DELETE OK as.String), 5 seconds)
          } catch {
            // Ignore timeouts
            case TimeoutException | InterruptedException =>
          }

          process.destroy()
          _state = Stopped()
        }
        case Stopping() | Stopped() =>
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
