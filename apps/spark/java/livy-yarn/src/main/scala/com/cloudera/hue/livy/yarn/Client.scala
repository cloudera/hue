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

import java.io.File

import com.cloudera.hue.livy.{LineBufferedProcess, LivyConf, Logging}
import org.apache.hadoop.fs.Path
import org.apache.hadoop.yarn.client.api.YarnClient
import org.apache.hadoop.yarn.conf.YarnConfiguration
import org.apache.hadoop.yarn.util.ConverterUtils

import scala.annotation.tailrec
import scala.concurrent.ExecutionContext

object Client {
  private lazy val regex = """Application report for (\w+)""".r.unanchored
}

class FailedToSubmitApplication extends Exception

class Client(livyConf: LivyConf) extends Logging {
  import Client._

  protected implicit def executor: ExecutionContext = ExecutionContext.global

  private[this] val yarnConf = new YarnConfiguration()
  private[this] val yarnClient = YarnClient.createYarnClient()
  val path = new Path(sys.env("HADOOP_CONF_DIR") + File.separator + YarnConfiguration.YARN_SITE_CONFIGURATION_FILE)
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


