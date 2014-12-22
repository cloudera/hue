package com.cloudera.hue.livy.yarn

import org.eclipse.jetty.server.Server
import org.eclipse.jetty.servlet.{DefaultServlet, ServletHolder}
import org.eclipse.jetty.webapp.WebAppContext
import org.scalatra.ScalatraServlet
import org.scalatra.servlet.{ScalatraListener, AsyncSupport}

import scala.concurrent.ExecutionContext

class WebServer extends Logging {
  val server = new Server(0)
  val context = new WebAppContext()
  var port = 0

  context.setContextPath("/")
  context.setResourceBase("src/main/com/cloudera/hue/livy/yarn")
  context.addEventListener(new ScalatraListener)

  context.addServlet(classOf[DefaultServlet], "/")

  context.setAttribute(AsyncSupport.ExecutionContextKey, ExecutionContext.global)

  server.setHandler(context)

  def start() = {
    //context.setContextPath("/")
    //context.setResourceBase(getClass.getClassLoader.getResource())
    server.start()
    port = server.getConnectors()(0).getLocalPort

    info("Starting RPC server on %s" format port)
  }

  def stop() = {
    context.stop()
    server.stop()
  }
}

class WebApp extends ScalatraServlet {
  get("/") {
    "hello world"
  }

  get("/hello") {
    "hello world2"
  }
}
