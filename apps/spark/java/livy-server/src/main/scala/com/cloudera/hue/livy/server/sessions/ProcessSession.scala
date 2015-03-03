package com.cloudera.hue.livy.server.sessions

import java.lang.ProcessBuilder.Redirect

import com.cloudera.hue.livy.{Logging, Utils}

import scala.collection.JavaConversions._
import scala.collection.mutable.ArrayBuffer
import scala.concurrent.Future

object ProcessSession extends Logging {
  def create(id: String, lang: String): Session = {
    val process = startProcess(id, lang)
    new ProcessSession(id, process)
  }

  // Loop until we've started a process with a valid port.
  private def startProcess(id: String, lang: String): Process = {
    val args = ArrayBuffer(
      "spark-submit",
      "--class",
      "com.cloudera.hue.livy.repl.Main"
    )

    sys.env.get("LIVY_REPL_JAVA_OPTS").foreach { case javaOpts =>
      args += "--driver-java-options"
      args += javaOpts
    }

    args += Utils.jarOfClass(getClass).head
    args += lang

    val pb = new ProcessBuilder(args)

    val callbackUrl = System.getProperty("livy.server.callback-url")
    pb.environment().put("LIVY_CALLBACK_URL", f"$callbackUrl/sessions/$id/callback")
    pb.environment().put("LIVY_PORT", "0")


    pb.redirectOutput(Redirect.INHERIT)
    pb.redirectError(Redirect.INHERIT)

    pb.start()

  }
}

private class ProcessSession(id: String, process: Process) extends WebSession(id) {

  override def stop(): Future[Unit] = {
    super.stop() andThen { case r =>
      // Make sure the process is reaped.
      process.waitFor()

      r
    }
  }
}
