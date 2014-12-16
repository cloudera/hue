package com.cloudera.hue.sparker.repl.yarn

import java.util
import java.util.EnumSet

import org.apache.hadoop.yarn.client.api.YarnClient
import org.apache.hadoop.yarn.conf.YarnConfiguration
import org.apache.hadoop.yarn.util.Records
import org.apache.hadoop.yarn.api.records._

object Client {
  def main(args: Array[String]) = {
    val yarnConf = new YarnConfiguration()
    val rmClient = YarnClient.createYarnClient()
    rmClient.init(yarnConf)

    rmClient.start()
    try {
      val appContext = rmClient.createApplication.getApplicationSubmissionContext
      val appId = appContext.getApplicationId

      val appName = "sparker-repl"
      val amPriority = 0
      val amQueue = "default"

      appContext.setApplicationName(appName)

      val priority: Priority = Records.newRecord(Class[Priority])
      priority.setPriority(amPriority)
      appContext.setPriority(priority)

      appContext.setQueue(amQueue)

      val amContainer: ContainerLaunchContext = Records.newRecord(Class[ContainerLaunchContext])
      appContext.setAMContainerSpec(amContainer)

      appContext.setUnmanagedAM(true)

      rmClient.submitApplication(appContext)

      var appReport = monitorApplication(
        appId,
        util.EnumSet.of(
          YarnApplicationState.ACCEPTED,
          YarnApplicationState.KILLED,
          YarnApplicationState.FAILED,
          YarnApplicationState.FINISHED
        ))

      if (appReport.getYarnApplicationState == YarnApplicationState.ACCEPTED) {
        val attemptReport = monitorCurrentAppAttempt(appId, YarnApplicationAttemptState.LAUNCHED)
        val attemptId = attemptReport.getApplicationAttemptId

        launchAM(attemptId)

        appReport = monitorApplication(
          appId,
          util.EnumSet.of(
            YarnApplicationState.KILLED,
            YarnApplicationState.FAILED,
            YarnApplicationState.FINISHED
          )
        )
      }

      val appState = appReport.getYarnApplicationState
      val appStatus = appReport.getFinalApplicationStatus

      if (YarnApplicationState.FINISHED == appState && FinalApplicationStatus.SUCCEEDED == appStatus) {
        0
      } else {
        1
      }
    } finally {
      rmClient.close()
    }
  }

  private def launchAM(attemptId: ApplicationAttemptId): Unit = {

  }

  private def monitorApplication(appId: ApplicationId, attemptState: util.EnumSet[YarnApplicationState]): ApplicationReport = {
    null
  }

  private def monitorCurrentAppAttempt(appId: ApplicationId, attemptState: YarnApplicationAttemptState): ApplicationAttemptReport = {
    null
  }


}
