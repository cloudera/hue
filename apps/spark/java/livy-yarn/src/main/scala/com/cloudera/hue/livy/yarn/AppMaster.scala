package com.cloudera.hue.livy.yarn

import com.cloudera.hue.livy.repl.ScalatraBootstrap
import com.cloudera.hue.livy.{WebServer, Logging}
import org.apache.hadoop.yarn.api.ApplicationConstants
import org.apache.hadoop.yarn.api.records.FinalApplicationStatus
import org.apache.hadoop.yarn.client.api.AMRMClient
import org.apache.hadoop.yarn.conf.YarnConfiguration
import org.apache.hadoop.yarn.util.ConverterUtils
import org.apache.spark.repl.Main
import org.scalatra.servlet.ScalatraListener

object AppMaster extends Logging {

  val SESSION_KIND = "livy-repl.session.kind"

  def main(args: Array[String]): Unit = {
    val lang = args(1)

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
    val service = new AppMasterService(yarnConfig, nodeHostString, lang)
    service.run()
  }

}

class AppMasterService(yarnConfig: YarnConfiguration, nodeHostString: String, lang: String) extends Logging {
  val webServer = new WebServer(0)
  val amRMClient = AMRMClient.createAMRMClient()
  amRMClient.init(yarnConfig)

  webServer.context.setResourceBase("src/main/com/cloudera/hue/livy/repl")
  webServer.context.addEventListener(new ScalatraListener)
  webServer.context.setInitParameter(ScalatraListener.LifeCycleKey, classOf[ScalatraBootstrap].getCanonicalName)
  webServer.context.setInitParameter(AppMaster.SESSION_KIND, lang)

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



