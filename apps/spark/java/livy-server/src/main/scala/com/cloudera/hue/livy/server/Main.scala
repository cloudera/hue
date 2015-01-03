package com.cloudera.hue.livy.server

import javax.servlet.ServletContext

import com.cloudera.hue.livy.WebServer
import org.scalatra._
import org.scalatra.servlet.ScalatraListener

object Main {
  def main(args: Array[String]): Unit = {
    val port = sys.env.getOrElse("PORT", "8998").toInt
    val server = new WebServer(port)

    server.context.setResourceBase("src/main/com/cloudera/hue/livy/server")
    server.context.setInitParameter(ScalatraListener.LifeCycleKey, classOf[ScalatraBootstrap].getCanonicalName)
    server.context.addEventListener(new ScalatraListener)

    server.start()
    server.join()
    server.stop()
  }
}

class ScalatraBootstrap extends LifeCycle {

  val sessionFactory = new YarnSessionFactory
  val sessionManager = new SessionManager(sessionFactory)

  override def init(context: ServletContext): Unit = {
    context.mount(new WebApp(sessionManager), "/*")
  }

  override def destroy(context: ServletContext): Unit = {
    sessionManager.close()
  }
}
