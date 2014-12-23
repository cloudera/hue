package com.cloudera.hue.livy.repl

import javax.servlet.ServletContext

import ch.qos.logback.access.jetty.RequestLogImpl
import com.cloudera.hue.livy.Logging
import com.cloudera.hue.livy.repl.interpreter.SparkInterpreter
import org.eclipse.jetty.server.{NCSARequestLog, Server}
import org.eclipse.jetty.server.handler.{RequestLogHandler, HandlerCollection}
import org.eclipse.jetty.servlet.DefaultServlet
import org.eclipse.jetty.webapp.WebAppContext
import org.scalatra.servlet.{AsyncSupport, ScalatraListener}
import org.scalatra.{LifeCycle, ScalatraServlet}

import scala.concurrent.ExecutionContext

class WebServer(var port: Int) extends Logging {
  val server = new Server(port)
  val context = new WebAppContext()

  context.setContextPath("/")
  context.setResourceBase("src/main/com/cloudera/hue/livy/repl")
  context.setInitParameter(ScalatraListener.LifeCycleKey, classOf[ScalatraBootstrap].getCanonicalName)
  context.addEventListener(new ScalatraListener)

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

  def start() = {
    server.start()
    port = server.getConnectors()(0).getLocalPort

    info("Starting RPC server on %s" format port)
  }

  def join() = {
    server.join()
  }

  def stop() = {
    context.stop()
    server.stop()
  }
}

class ScalatraBootstrap extends LifeCycle {

  //val system = ActorSystem()
  val sparkInterpreter = new SparkInterpreter

  override def init(context: ServletContext): Unit = {
    context.mount(new LivyApp(sparkInterpreter), "/*")
  }

  override def destroy(context: ServletContext): Unit = {
    sparkInterpreter.close()
    //system.shutdown()
  }
}
