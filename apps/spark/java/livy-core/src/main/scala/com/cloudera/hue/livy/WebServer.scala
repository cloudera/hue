package com.cloudera.hue.livy

import java.net.{InetAddress, InetSocketAddress}
import javax.servlet.ServletContextListener

import ch.qos.logback.access.jetty.RequestLogImpl
import org.eclipse.jetty.server.Server
import org.eclipse.jetty.server.handler.{HandlerCollection, RequestLogHandler}
import org.eclipse.jetty.servlet.{ServletContextHandler, DefaultServlet}
import org.scalatra.servlet.AsyncSupport

import scala.concurrent.ExecutionContext

class WebServer(var host: String, var port: Int) extends Logging {
  val address = new InetSocketAddress(host, port)
  val server = new Server(address)

  server.setGracefulShutdown(1000)
  server.setStopAtShutdown(true)

  val context = new ServletContextHandler()

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

  def start() = {
    server.start()

    val connector = server.getConnectors()(0)

    host = connector.getHost
    if (host == "0.0.0.0") {
      host = InetAddress.getLocalHost.getHostAddress
    }
    port = connector.getLocalPort

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

