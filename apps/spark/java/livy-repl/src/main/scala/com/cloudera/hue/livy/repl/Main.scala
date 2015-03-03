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

import _root_.scala.annotation.tailrec
import _root_.scala.concurrent.duration._
import _root_.scala.concurrent.{Await, ExecutionContext}

object Main extends Logging {

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
      val replUrl = s"http://${server.host}:${server.port}"
      println(s"Starting livy-repl on $replUrl")
      System.setProperty("livy.repl.url", replUrl)

      server.join()
      server.stop()
    } finally {
      // Make sure to close all our outstanding http requests.
      Http.shutdown()
    }
  }
}

class ScalatraBootstrap extends LifeCycle with Logging {

  protected implicit def executor: ExecutionContext = ExecutionContext.global
  protected implicit def jsonFormats: Formats = DefaultFormats

  var session: Session = null

  override def init(context: ServletContext): Unit = {
    session = context.getInitParameter(Main.SESSION_KIND) match {
      case Main.PYTHON_SESSION => PythonSession.createPySpark()
      case Main.PYSPARK_SESSION => PythonSession.createPySpark()
      case Main.SCALA_SESSION => SparkSession.create()
      case Main.SPARK_SESSION => SparkSession.create()
    }

    context.mount(new WebApp(session), "/*")

    val callbackUrl = Option(System.getProperty("livy.repl.callback-url"))
      .orElse(sys.env.get("LIVY_CALLBACK_URL"))

    // See if we want to notify someone that we've started on a url
    callbackUrl.foreach(notifyCallback)
  }

  override def destroy(context: ServletContext): Unit = {
    if (session != null) {
      Await.result(session.close(), Duration.Inf)
    }
  }

  private def notifyCallback(callbackUrl: String): Unit = {
    info(s"Notifying $callbackUrl that we're up")

    Future {
      session.waitForStateChange(Session.Starting())

      // Wait for our url to be discovered.
      val replUrl = waitForReplUrl()

      var req = url(callbackUrl).setContentType("application/json", "UTF-8")
      req = req << write(Map("url" -> replUrl))

      val rep = Http(req OK as.String)
      rep.onFailure {
        case _ => System.exit(1)
      }

      Await.result(rep, 10 seconds)
    }
  }

  /** Spin until The server may start up  */
  @tailrec
  private def waitForReplUrl(): String = {
    val replUrl = System.getProperty("livy.repl.url")
    if (replUrl == null) {
      Thread.sleep(10)
      waitForReplUrl()
    } else {
      replUrl
    }
  }
}