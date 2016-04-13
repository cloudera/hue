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

package com.cloudera.hue.livy.spark.interactive

import com.cloudera.hue.livy.sessions.Kind

case class CreateInteractiveRequest(
    kind: Kind,
    proxyUser: Option[String] = None,
    jars: Option[String] = None,
    pyFiles: List[String] = List(),
    files: Option[String] = None,
    driverMemory: Option[String] = None,
    driverCores: Option[Int] = None,
    executorMemory: Option[String] = None,
    executorCores: Option[Int] = None,
    totalExecutorCores: Option[Int] = None,
    numExecutors: Option[Int] = None,
    archives: List[String] = List(),
    queue: Option[String] = None,
    name: Option[String] = None,
    conf: Map[String, String] = Map())
