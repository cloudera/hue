package com.cloudera.hue.livy.yarn

import org.apache.hadoop.net.NetUtils
import org.apache.hadoop.yarn.api.ApplicationConstants
import org.apache.hadoop.yarn.api.records.FinalApplicationStatus
import org.apache.hadoop.yarn.client.api.AMRMClient
import org.apache.hadoop.yarn.conf.YarnConfiguration
import org.apache.hadoop.yarn.util.ConverterUtils
import org.eclipse.jetty.server.Server
import org.eclipse.jetty.servlet.DefaultServlet
import org.eclipse.jetty.webapp.WebAppContext
import org.scalatra.servlet.{AsyncSupport, ScalatraListener}

import scala.concurrent.ExecutionContext

object AppMaster extends Logging {

  def main(args: Array[String]): Unit = {
    val containerIdString = System.getenv(ApplicationConstants.Environment.CONTAINER_ID.toString)
    info("got container id: %s" format containerIdString)
    val containerId = ConverterUtils.toContainerId(containerIdString)

    val appAttemptId = containerId.getApplicationAttemptId
    info("got app attempt id: %s" format containerIdString)

    val nodeHostString = System.getenv(ApplicationConstants.Environment.NM_HOST.toString)
    info("got node manager host: %s" format nodeHostString)

    val nodePortString = System.getenv(ApplicationConstants.Environment.NM_PORT.toString)
    info("got node manager port: %s" format nodeHostString)

    val yarnConfig = new YarnConfiguration
    val amRMClient = AMRMClient.createAMRMClient()
    amRMClient.init(yarnConfig)
    amRMClient.start()

    try {
      val server = new Server(0)
      val context = new WebAppContext()

      context.setContextPath("/")
      context.setResourceBase("src/main/com/cloudera/hue/livy/repl")
      context.addEventListener(new ScalatraListener)

      context.addServlet(classOf[DefaultServlet], "/")

      context.setAttribute(AsyncSupport.ExecutionContextKey, ExecutionContext.global)

      server.setHandler(context)

      server.start()

      // Now that the server is up and running register it with YARN.
      val appMasterHostname = NetUtils.getHostname
      val appMasterRpcPort = server.getConnectors()(0).getLocalPort
      val appMasterTrackingUrl = ""

      info("Starting RPC server on %s:%s" format(appMasterHostname, appMasterRpcPort))
      info("Tracking URL: %s" format appMasterTrackingUrl)

      val response = amRMClient.registerApplicationMaster(appMasterHostname, appMasterRpcPort, appMasterTrackingUrl)

      val maxMem = response.getMaximumResourceCapability.getMemory
      info("max mem capacity on this cluster: %s" format maxMem)

      val maxVCores = response.getMaximumResourceCapability.getVirtualCores
      info("max vcore capacity on this cluster: %s" format maxMem)

      // Finallay, wait for the web service to shut down.
      server.join()

    } finally {
      val appStatus = FinalApplicationStatus.SUCCEEDED
      val appMessage = "wee"

      amRMClient.unregisterApplicationMaster(appStatus, appMessage, null)
      amRMClient.stop()
    }
  }

}
