package com.cloudera.hue.livy.server

import javax.servlet.ServletContext

import com.cloudera.hue.livy.WebServer
import org.scalatra._
import org.scalatra.servlet.ScalatraListener

object Main {

  val SESSION_KIND = "livy.session.kind"
  val PROCESS_SESSION = "process"
  val YARN_SESSION = "yarn"

  def main(args: Array[String]): Unit = {

    if (args.length != 1) {
      println("Must specify either `process` or `yarn` for the session kind")
      sys.exit(1)
    }

    val session_kind = args(0)

    session_kind match {
      case PROCESS_SESSION | YARN_SESSION =>
      case _ =>
        println("Unknown session kind: " + session_kind)
        sys.exit(1)
    }

    val port = sys.env.getOrElse("PORT", "8998").toInt
    val server = new WebServer(port)


    server.context.setResourceBase("src/main/com/cloudera/hue/livy/server")
    server.context.setInitParameter(ScalatraListener.LifeCycleKey, classOf[ScalatraBootstrap].getCanonicalName)
    server.context.addEventListener(new ScalatraListener)
    server.context.setInitParameter(SESSION_KIND, session_kind)

    server.start()
    server.join()
    server.stop()
  }
}

class ScalatraBootstrap extends LifeCycle {

  var sessionManager: SessionManager = null

  override def init(context: ServletContext): Unit = {
    val sessionFactory = context.getInitParameter(Main.SESSION_KIND) match {
      case Main.PROCESS_SESSION => new ProcessSessionFactory
      case Main.YARN_SESSION => new YarnSessionFactory
    }

    sessionManager = new SessionManager(sessionFactory)

    context.mount(new WebApp(sessionManager), "/*")
  }

  override def destroy(context: ServletContext): Unit = {
    sessionManager.close()
  }
}
