package com.cloudera.hue.sparker.repl

import java.io.StringWriter

import org.eclipse.jetty.server.Server
import org.eclipse.jetty.servlet.DefaultServlet
import org.eclipse.jetty.webapp.WebAppContext
import org.scalatra.servlet.ScalatraListener

object Main {
  def main(args: Array[String]): Unit = {
    org.apache.spark.repl.Main.interp = new SparkerILoop(Console.in, new StringWriter)
    org.apache.spark.repl.Main.interp.process(args)
  }
}

/*
object Main {
  def main(args: Array[String]): Unit = {
    val port = 8087
    val server = new Server(port)
    val context = new WebAppContext()
    context.setContextPath("/")
    context.setResourceBase("src/main/com/cloudera/hue/sparker/repl")
    context.addEventListener(new ScalatraListener)
    context.addServlet(classOf[DefaultServlet], "/")

    server.setHandler(context)

    server.start()
    server.join()
  }
}
*/
