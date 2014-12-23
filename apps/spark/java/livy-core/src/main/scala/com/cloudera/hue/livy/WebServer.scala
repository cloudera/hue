package com.cloudera.hue.livy

import javax.servlet.{Servlet, ServletContextListener}

import ch.qos.logback.access.jetty.RequestLogImpl
import org.eclipse.jetty.server.Server
import org.eclipse.jetty.server.handler.{HandlerCollection, RequestLogHandler}
import org.eclipse.jetty.servlet.DefaultServlet
import org.eclipse.jetty.webapp.WebAppContext
import org.scalatra.servlet.AsyncSupport

import scala.concurrent.ExecutionContext

class WebServer(var port: Int) extends Logging {
  val server = new Server(port)
  val context = new WebAppContext()

  context.setContextPath("/")

  context.addServlet(classOf[DefaultServlet], "/")

  context.setAttribute(AsyncSupport.ExecutionContextKey, ExecutionContext.global)

  val handlers = new HandlerCollection
  handlers.addHandler(context)

  // configure the access log
  val requestLogHandler = new RequestLogHandler
  val requestLog = new RequestLogImpl
  requestLog.setResource("/logback-access.xml")
  requestLogHandler.setRequestLog(requestLog)
  handlers.addHandler(requestLogHandler)

  server.setHandler(handlers)

  def addEventListener(listener: ServletContextListener) = {
    context.addEventListener(listener)
  }

  def addServlet(servlet: Servlet) = {

  }

  def start() = {
    server.start()
    port = server.getConnectors()(0).getLocalPort

    info("Starting server on %s" format port)
  }

  def join() = {
    server.join()
  }

  def stop() = {
    context.stop()
    server.stop()
  }
}

