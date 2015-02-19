package com.cloudera.hue.livy.repl

import javax.servlet.ServletContext

import com.cloudera.hue.livy.repl.python.PythonSession
import com.cloudera.hue.livy.repl.scala.SparkSession
import com.cloudera.hue.livy.{Logging, WebServer}
import dispatch._
import org.json4s.jackson.Serialization.write
import org.json4s.{DefaultFormats, Formats}
import org.scalatra.LifeCycle
import org.scalatra.servlet.ScalatraListener

import _root_.scala.concurrent.duration._
import _root_.scala.concurrent.{Await, ExecutionContext}

object Main extends Logging {

  protected implicit def executor: ExecutionContext = ExecutionContext.global
  protected implicit def jsonFormats: Formats = DefaultFormats

  val SESSION_KIND = "livy.repl.session.kind"
  val PYTHON_SESSION = "python"
  val PYSPARK_SESSION = "pyspark"
  val SCALA_SESSION = "scala"
  val SPARK_SESSION = "spark"

  def main(args: Array[String]): Unit = {

    val host = Option(System.getProperty("livy.repl.host"))
      .orElse(sys.env.get("LIVY_HOST"))
      .getOrElse("0.0.0.0")

    val port = Option(System.getProperty("livy.repl.port"))
      .orElse(sys.env.get("LIVY_PORT"))
      .getOrElse("8999").toInt

    val callbackUrl = Option(System.getProperty("livy.repl.callback-url"))
      .orElse(sys.env.get("LIVY_CALLBACK_URL"))

    if (args.length != 1) {
      println("Must specify either `python`/`pyspark`/`scala/`spark` for the session kind")
      sys.exit(1)
    }

    val session_kind = args(0)

    session_kind match {
      case PYTHON_SESSION | PYSPARK_SESSION | SCALA_SESSION | SPARK_SESSION =>
      case _ =>
        println("Unknown session kind: " + session_kind)
        sys.exit(1)
    }

    val server = new WebServer(host, port)

    server.context.setResourceBase("src/main/com/cloudera/hue/livy/repl")
    server.context.addEventListener(new ScalatraListener)
    server.context.setInitParameter(ScalatraListener.LifeCycleKey, classOf[ScalatraBootstrap].getCanonicalName)
    server.context.setInitParameter(SESSION_KIND, session_kind)

    server.start()

    try {
      println("Starting livy-repl on port %s" format server.port)

      // See if we want to notify someone that we've started on a url
      callbackUrl.foreach { case callbackUrl_ =>
        info(f"Notifying $callbackUrl_ that we're up")

        var req = url(callbackUrl_).setContentType("application/json", "UTF-8")
        req = req << write(Map(
          "url" -> s"http://${server.host}:${server.port}"
        ))

        val rep = Http(req OK as.String)
        rep.onFailure { case _ => server.stop() }

        Await.result(rep, 10 seconds)
      }

    } finally {
      server.join()
      server.stop()

      // Make sure to close all our outstanding http requests.
      Http.shutdown()
    }
  }
}

class ScalatraBootstrap extends LifeCycle {

  var session: Session = null

  override def init(context: ServletContext): Unit = {
    session = context.getInitParameter(Main.SESSION_KIND) match {
      case Main.PYTHON_SESSION => PythonSession.createPySpark()
      case Main.PYSPARK_SESSION => PythonSession.createPySpark()
      case Main.SCALA_SESSION => SparkSession.create()
      case Main.SPARK_SESSION => SparkSession.create()
    }

    context.mount(new WebApp(session), "/*")
  }

  override def destroy(context: ServletContext): Unit = {
    if (session != null) {
      Await.result(session.close(), Duration.Inf)
    }
  }
}