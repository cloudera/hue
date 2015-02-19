package com.cloudera.hue.livy.server

import javax.servlet.ServletContext

import com.cloudera.hue.livy.{LivyConf, WebServer}
import org.scalatra._
import org.scalatra.servlet.ScalatraListener

object Main {

  val SESSION_KIND = "livy-server.session.kind"
  val THREAD_SESSION = "thread"
  val PROCESS_SESSION = "process"
  val YARN_SESSION = "yarn"

  def main(args: Array[String]): Unit = {
    val host = Option(System.getProperty("livy.server.host"))
      .getOrElse("0.0.0.0")

    val port = Option(System.getProperty("livy.server.port"))
      .getOrElse("8998").toInt

    if (args.length != 1) {
      println("Must specify either `thread`, `process`, or `yarn` for the session kind")
      sys.exit(1)
    }

    val session_kind = args(0)

    session_kind match {
      case THREAD_SESSION | PROCESS_SESSION | YARN_SESSION =>
      case _ =>
        println("Unknown session kind: " + session_kind)
        sys.exit(1)
    }

    val server = new WebServer(host, port)

    server.context.setResourceBase("src/main/com/cloudera/hue/livy/server")
    server.context.setInitParameter(ScalatraListener.LifeCycleKey, classOf[ScalatraBootstrap].getCanonicalName)
    server.context.addEventListener(new ScalatraListener)
    server.context.setInitParameter(SESSION_KIND, session_kind)

    server.start()

    try {
      System.setProperty("livy.server.callback-url", f"http://${server.host}:${server.port}")
    } finally {
      server.join()
      server.stop()

      // Make sure to close all our outstanding http requests.
      dispatch.Http.shutdown()
    }
  }
}

class ScalatraBootstrap extends LifeCycle {

  var sessionManager: SessionManager = null

  override def init(context: ServletContext): Unit = {
    val livyConf = new LivyConf()

    val sessionFactory = context.getInitParameter(Main.SESSION_KIND) match {
      case Main.THREAD_SESSION => new ThreadSessionFactory
      case Main.PROCESS_SESSION => new ProcessSessionFactory
      case Main.YARN_SESSION => new YarnSessionFactory(livyConf)
    }

    sessionManager = new SessionManager(sessionFactory)

    context.mount(new WebApp(sessionManager), "/*")
  }

  override def destroy(context: ServletContext): Unit = {
    if (sessionManager != null) {
      sessionManager.shutdown()
    }
  }
}
