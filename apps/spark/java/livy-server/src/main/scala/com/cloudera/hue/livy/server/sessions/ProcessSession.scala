package com.cloudera.hue.livy.server.sessions

import java.lang.ProcessBuilder.Redirect

import com.cloudera.hue.livy.Logging

import scala.annotation.tailrec
import scala.concurrent.Future
import scala.io.Source

object ProcessSession extends Logging {
  val LIVY_HOME = System.getenv("LIVY_HOME")
  val LIVY_REPL = LIVY_HOME + "/bin/livy-repl"

  def create(id: String, lang: String): Session = {
    val (process, port) = startProcess(lang)
    new ProcessSession(id, process, port)
  }

  // Loop until we've started a process with a valid port.
  private def startProcess(lang: String): (Process, Int) = {
    val regex = """Starting livy-repl on port (\d+)""".r

    @tailrec
    def parsePort(lines: Iterator[String]): Option[Int] = {
      if (lines.hasNext) {
        val line = lines.next()
        info("shell output: %s" format line)

        line match {
          case regex(port_) => Some(port_.toInt)
          case _ => parsePort(lines)
        }
      } else {
        None
      }
    }

    def startProcess(lang: String): (Process, Int) = {
      val pb = new ProcessBuilder(LIVY_REPL, lang)
      pb.environment().put("PORT", "0")
      pb.redirectError(Redirect.INHERIT)
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
          throw new SessionFailedToStart("Couldn't start livy-repl")
      }
    }

    startProcess(lang)
  }
}

private class ProcessSession(id: String, process: Process, port: Int) extends WebSession(id, "localhost", port) {

  override def stop(): Future[Unit] = {
    super.stop() andThen { case r =>
      // Make sure the process is reaped.
      process.waitFor()

      r
    }
  }
}
