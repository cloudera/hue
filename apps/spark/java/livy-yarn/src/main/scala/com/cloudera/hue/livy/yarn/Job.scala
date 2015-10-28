package com.cloudera.hue.livy.yarn

import org.apache.hadoop.yarn.api.records.{FinalApplicationStatus, YarnApplicationState, ApplicationId}
import org.apache.hadoop.yarn.client.api.YarnClient

class Job(yarnClient: YarnClient, appId: ApplicationId) {
  def waitForFinish(timeoutMs: Long): Option[ApplicationState] = {
    val startTimeMs = System.currentTimeMillis()

    while (System.currentTimeMillis() - startTimeMs < timeoutMs) {
      val status = getStatus
      status match {
        case ApplicationState.SuccessfulFinish() | ApplicationState.UnsuccessfulFinish() =>
          return Some(status)
        case _ =>
      }

      Thread.sleep(1000)
    }

    None
  }

  def waitForStatus(status: ApplicationState, timeoutMs: Long): Option[ApplicationState] = {
    val startTimeMs = System.currentTimeMillis()

    while (System.currentTimeMillis() - startTimeMs < timeoutMs) {
      if (getStatus == status) {
        return Some(status)
      }

      Thread.sleep(1000)
    }

    None
  }

  def waitForRPC(timeoutMs: Long): Option[(String, Int)] = {
    waitForStatus(ApplicationState.Running(), timeoutMs)

    val startTimeMs = System.currentTimeMillis()

    while (System.currentTimeMillis() - startTimeMs < timeoutMs) {
      val statusResponse = yarnClient.getApplicationReport(appId)

      (statusResponse.getHost, statusResponse.getRpcPort) match {
        case ("N/A", _) | (_, -1) =>
        case (hostname, port) => return Some((hostname, port))
      }
    }

    None
  }

  def getHost: String = {
    val statusResponse = yarnClient.getApplicationReport(appId)
    statusResponse.getHost
  }

  def getPort: Int = {
    val statusResponse = yarnClient.getApplicationReport(appId)
    statusResponse.getRpcPort
  }

  def getStatus: ApplicationState = {
    val statusResponse = yarnClient.getApplicationReport(appId)
    convertState(statusResponse.getYarnApplicationState, statusResponse.getFinalApplicationStatus)
  }

  def stop(): Unit = {
    yarnClient.killApplication(appId)
  }

  private def convertState(state: YarnApplicationState, status: FinalApplicationStatus): ApplicationState = {
    (state, status) match {
      case (YarnApplicationState.FINISHED, FinalApplicationStatus.SUCCEEDED) => ApplicationState.SuccessfulFinish()
      case (YarnApplicationState.FINISHED, _) |
           (YarnApplicationState.KILLED, _) |
           (YarnApplicationState.FAILED, _) => ApplicationState.UnsuccessfulFinish()
      case (YarnApplicationState.NEW, _) |
           (YarnApplicationState.NEW_SAVING, _) |
           (YarnApplicationState.SUBMITTED, _) => ApplicationState.New()
      case (YarnApplicationState.RUNNING, _) => ApplicationState.Running()
      case (YarnApplicationState.ACCEPTED, _) => ApplicationState.Accepted()
    }
  }
}
