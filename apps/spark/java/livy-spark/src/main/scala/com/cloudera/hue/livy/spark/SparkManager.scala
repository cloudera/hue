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

package com.cloudera.hue.livy.spark

import com.cloudera.hue.livy.{Utils, LivyConf}
import com.cloudera.hue.livy.LivyConf.{Process, Yarn}
import com.cloudera.hue.livy.sessions.SessionManager
import com.cloudera.hue.livy.sessions.batch.BatchSession
import com.cloudera.hue.livy.sessions.interactive.InteractiveSession
import com.cloudera.hue.livy.spark.batch.{BatchSessionProcessFactory, BatchSessionYarnFactory}
import com.cloudera.hue.livy.spark.interactive.{InteractiveSessionProcessFactory, InteractiveSessionYarnFactory}
import com.cloudera.hue.livy.yarn.Client

import scala.io.Source

object SparkManager {
  def apply(livyConf: LivyConf): SparkManager = {
    val userConfigurableOptions = loadSparkUserConfigurableOptions()
    val processFactory = new SparkProcessBuilderFactory(livyConf, userConfigurableOptions)

    livyConf.sessionKind() match {
      case Process() => new SparkProcessManager(processFactory)
      case Yarn() => new SparkYarnManager(processFactory)
    }
  }

  private val SparkUserConfig = "spark-user-configurable-options.conf"
  private val DefaultSparkUserConfig = "default-spark-user-configurable-options.conf"

  private def loadSparkUserConfigurableOptions(): Set[String] = {
    Utils.getLivyConfigFile(SparkUserConfig)
      .map(Source.fromFile)
      .orElse {
        Option(getClass.getResourceAsStream(DefaultSparkUserConfig))
          .map(Source.fromInputStream)
      }
      .map { source =>
        source.getLines()
          .map(_.trim)
          .filter(!_.startsWith("//"))
          .toSet
      }
      .getOrElse(Set())
  }
}

trait SparkManager {
  def batchManager: SessionManager[BatchSession]

  def interactiveManager: SessionManager[InteractiveSession]

  def shutdown()
}

private class SparkProcessManager(processFactory: SparkProcessBuilderFactory) extends SparkManager {
  private[this] val batchFactory = new BatchSessionProcessFactory(processFactory)
  private[this] val interactiveFactory = new InteractiveSessionProcessFactory(processFactory)

  val batchManager = new SessionManager(processFactory.livyConf, batchFactory)

  val interactiveManager = new SessionManager(processFactory.livyConf, interactiveFactory)

  override def shutdown(): Unit = {
    batchManager.shutdown()
    interactiveManager.shutdown()
  }
}

private class SparkYarnManager(processFactory: SparkProcessBuilderFactory) extends SparkManager {
  private[this] val client = new Client(processFactory.livyConf)
  private[this] val batchFactory = new BatchSessionYarnFactory(client, processFactory)
  private[this] val interactiveFactory = new InteractiveSessionYarnFactory(client, processFactory)

  val batchManager = new SessionManager(processFactory.livyConf, batchFactory)

  val interactiveManager = new SessionManager(processFactory.livyConf, interactiveFactory)

  override def shutdown(): Unit = {
    batchManager.shutdown()
    interactiveManager.shutdown()
    client.close()
  }
}