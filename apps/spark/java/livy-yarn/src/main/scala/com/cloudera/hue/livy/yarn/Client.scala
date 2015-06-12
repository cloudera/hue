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

package com.cloudera.hue.livy.yarn

import java.io.{InputStream, BufferedReader, InputStreamReader}

import com.cloudera.hue.livy.yarn.Client._
import com.cloudera.hue.livy.{Utils, LineBufferedProcess, LivyConf, Logging}
import org.apache.hadoop.yarn.api.records.{ApplicationId, FinalApplicationStatus, YarnApplicationState}
import org.apache.hadoop.yarn.client.api.YarnClient
import org.apache.hadoop.yarn.conf.YarnConfiguration
import org.apache.hadoop.yarn.util.ConverterUtils
import org.apache.hadoop.fs.Path

import scala.annotation.tailrec
import scala.concurrent.ExecutionContext
import scala.io.Source

object Client {
  private lazy val regex = """Application report for (\w+)""".r.unanchored

  sealed trait ApplicationStatus
  case class New() extends ApplicationStatus
  case class Accepted() extends ApplicationStatus
  case class Running() extends ApplicationStatus
  case class SuccessfulFinish() extends ApplicationStatus
  case class UnsuccessfulFinish() extends ApplicationStatus
}

class FailedToSubmitApplication extends Exception

class Client(livyConf: LivyConf) extends Logging {
  import Client._

  protected implicit def executor: ExecutionContext = ExecutionContext.global

  private[this] val yarnConf = new YarnConfiguration()
  private[this] val yarnClient = YarnClient.createYarnClient()
  val path = new Path(sys.env("HADOOP_CONF_DIR") + YarnConfiguration.YARN_SITE_CONFIGURATION_FILE)
  yarnConf.addResource(path)
  val rm_address = yarnConf.get(YarnConfiguration.RM_ADDRESS)
  info(s"Resource Manager address: $rm_address")

  yarnClient.init(yarnConf)
  yarnClient.start()

  def getJobFromProcess(process: LineBufferedProcess): Job = {
    parseApplicationId(process.inputIterator) match {
      case Some(appId) => new Job(yarnClient, ConverterUtils.toApplicationId(appId))
      case None => throw new FailedToSubmitApplication
    }
  }

  def close() = {
    yarnClient.close()
  }

  @tailrec
  private def parseApplicationId(lines: Iterator[String]): Option[String] = {
    if (lines.hasNext) {
      val line = lines.next()
      line match {
        case regex(applicationId) => Some(applicationId)
        case _ => parseApplicationId(lines)
      }
    } else {
      None
    }
  }
}

class Job(yarnClient: YarnClient, appId: ApplicationId) {
  def waitForFinish(timeoutMs: Long): Option[ApplicationStatus] = {
    val startTimeMs = System.currentTimeMillis()

    while (System.currentTimeMillis() - startTimeMs < timeoutMs) {
      val status = getStatus
      status match {
        case SuccessfulFinish() | UnsuccessfulFinish() =>
          return Some(status)
        case _ =>
      }

      Thread.sleep(1000)
    }

    None
  }

  def waitForStatus(status: ApplicationStatus, timeoutMs: Long): Option[ApplicationStatus] = {
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
    waitForStatus(Running(), timeoutMs)

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

  def getStatus: ApplicationStatus = {
    val statusResponse = yarnClient.getApplicationReport(appId)
    convertState(statusResponse.getYarnApplicationState, statusResponse.getFinalApplicationStatus)
  }

  def stop(): Unit = {
    yarnClient.killApplication(appId)
  }

  private def convertState(state: YarnApplicationState, status: FinalApplicationStatus): ApplicationStatus = {
    (state, status) match {
      case (YarnApplicationState.FINISHED, FinalApplicationStatus.SUCCEEDED) => SuccessfulFinish()
      case (YarnApplicationState.FINISHED, _) |
           (YarnApplicationState.KILLED, _) |
           (YarnApplicationState.FAILED, _) => UnsuccessfulFinish()
      case (YarnApplicationState.NEW, _) |
           (YarnApplicationState.NEW_SAVING, _) |
           (YarnApplicationState.SUBMITTED, _) => New()
      case (YarnApplicationState.RUNNING, _) => Running()
      case (YarnApplicationState.ACCEPTED, _) => Accepted()
    }
  }
}
