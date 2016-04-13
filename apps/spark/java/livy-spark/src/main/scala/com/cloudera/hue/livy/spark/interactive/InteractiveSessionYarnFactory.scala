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

import com.cloudera.hue.livy.sessions.interactive.InteractiveSession
import com.cloudera.hue.livy.spark.{SparkProcess, SparkProcessBuilderFactory}
import com.cloudera.hue.livy.yarn.Client

import scala.concurrent.ExecutionContext

class InteractiveSessionYarnFactory(client: Client, processFactory: SparkProcessBuilderFactory)
  extends InteractiveSessionFactory(processFactory) {

  implicit def executor: ExecutionContext = ExecutionContext.global

  protected override def create(id: Int,
                                process: SparkProcess,
                                request: CreateInteractiveRequest): InteractiveSession = {
    InteractiveSessionYarn(client, id, process, request)
  }

  override def sparkBuilder(id: Int, request: CreateInteractiveRequest) = {
    val builder = super.sparkBuilder(id, request)
    builder.master("yarn-cluster")
    builder
  }
 }
