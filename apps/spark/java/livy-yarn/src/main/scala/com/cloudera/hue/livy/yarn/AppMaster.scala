package com.cloudera.hue.livy.yarn

import org.apache.hadoop.net.NetUtils
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
    info("got node manager port: %s" format nodeHostString)

    val yarnConfig = new YarnConfiguration
    val amRMClient = AMRMClient.createAMRMClient()
    amRMClient.init(yarnConfig)
    amRMClient.start()

    try {
      val appMasterHostname = NetUtils.getHostname
      val appMasterRpcPort = -1
      val appMasterTrackingUrl = ""

      val response = amRMClient.registerApplicationMaster(appMasterHostname, appMasterRpcPort, appMasterTrackingUrl)

      val maxMem = response.getMaximumResourceCapability.getMemory
      info("max mem capacity on this cluster: %s" format maxMem)

      val maxVCores = response.getMaximumResourceCapability.getVirtualCores
      info("max vcore capacity on this cluster: %s" format maxMem)
    } finally {
      val appStatus = FinalApplicationStatus.SUCCEEDED
      val appMessage = "wee"

      amRMClient.unregisterApplicationMaster(appStatus, appMessage, null)
      amRMClient.stop()
    }
  }

}
