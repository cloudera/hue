package com.cloudera.hue.livy.yarn

import org.apache.hadoop.yarn.api.ApplicationConstants
import org.apache.hadoop.yarn.api.records.FinalApplicationStatus
import org.apache.hadoop.yarn.client.api.AMRMClient
import org.apache.hadoop.yarn.conf.YarnConfiguration
import org.apache.hadoop.yarn.util.ConverterUtils

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
    info("got node manager port: %s" format nodePortString)

    val yarnConfig = new YarnConfiguration()
    val service = new AppMasterService(yarnConfig, nodeHostString)
    service.run()
  }

}

class AppMasterService(yarnConfig: YarnConfiguration, nodeHostString: String) extends Logging {
  val webServer = new WebServer
  val amRMClient = AMRMClient.createAMRMClient()
  amRMClient.init(yarnConfig)

  def run(): Unit = {
    webServer.start()
    try {
      amRMClient.start()

      try {
        // Now that the server is up and running register it with YARN.
        val response = amRMClient.registerApplicationMaster(nodeHostString, webServer.port, "%s:%s" format(nodeHostString, webServer.port))

        val maxMem = response.getMaximumResourceCapability.getMemory
        info("max mem capacity on this cluster: %s" format maxMem)

        val maxVCores = response.getMaximumResourceCapability.getVirtualCores
        info("max vcore capacity on this cluster: %s" format maxMem)

        var isShutdown = false

        while (!isShutdown) {
          try {
            Thread.sleep(1000)
          } catch {
            case e: InterruptedException => {
              isShutdown = true
            }
          }
        }
      } finally {
        val appStatus = FinalApplicationStatus.SUCCEEDED
        val appMessage = "wee"

        amRMClient.unregisterApplicationMaster(appStatus, appMessage, null)
        amRMClient.stop()
      }
    } finally {
      webServer.stop()
    }
  }
}



