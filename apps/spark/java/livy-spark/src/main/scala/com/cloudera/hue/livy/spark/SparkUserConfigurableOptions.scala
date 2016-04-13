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

import java.io.File

import com.cloudera.hue.livy.Utils

import scala.io.Source

object SparkUserConfigurableOptions {
  def apply(): Set[String] = {
    val file = Utils.getLivyConfDir()
      .map(path => new File(path, "spark-user-configurable-options.conf"))
      .get

    apply(file)
  }

  def apply(configFile: File): Set[String] = {
    Source.fromFile(configFile).getLines()
      .map(_.trim)
      .filter(_.startsWith("//"))
      .toSet
  }
}
