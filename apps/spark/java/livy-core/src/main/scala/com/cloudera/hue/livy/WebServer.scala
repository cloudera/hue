/*
 * Licensed to Cloudera, Inc. under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  Cloudera, Inc. licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package com.cloudera.hue.livy

import java.net.{InetAddress, InetSocketAddress}
import javax.servlet.ServletContextListener

import ch.qos.logback.access.jetty.RequestLogImpl
import org.eclipse.jetty.server.{NetworkConnector, Server}
import org.eclipse.jetty.server.handler.{HandlerCollection, RequestLogHandler}
import org.eclipse.jetty.servlet.{ServletContextHandler, DefaultServlet}
import org.scalatra.servlet.AsyncSupport

import scala.concurrent.ExecutionContext

class WebServer(var host: String, var port: Int) extends Logging {
  val address = new InetSocketAddress(host, port)
  val server = new Server(address)

  server.setStopTimeout(1000)
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

    val connector = server.getConnectors()(0).asInstanceOf[NetworkConnector]

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

