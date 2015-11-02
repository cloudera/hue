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

package com.cloudera.hue.livy.spark.batch

import java.io.FileWriter
import java.nio.file.{Files, Path}
import java.util.concurrent.TimeUnit

import com.cloudera.hue.livy.sessions.SessionState
import com.cloudera.hue.livy.spark.SparkProcessBuilderFactory
import com.cloudera.hue.livy.{LivyConf, Utils}
import org.scalatest.{BeforeAndAfterAll, FunSpec, ShouldMatchers}

import scala.concurrent.duration.Duration

class BatchProcessSpec
  extends FunSpec
  with BeforeAndAfterAll
  with ShouldMatchers {

  val script: Path = {
    val script = Files.createTempFile("livy-test", ".py")
    script.toFile.deleteOnExit()
    val writer = new FileWriter(script.toFile)
    try {
      writer.write(
        """
          |print "hello world"
        """.stripMargin)
    } finally {
      writer.close()
    }
    script
  }

  describe("A Batch process") {
    it("should create a process") {
      val req = CreateBatchRequest(
        file = script.toString
      )

      val livyConf = new LivyConf()
      val builder = new BatchSessionProcessFactory(new SparkProcessBuilderFactory(livyConf))
      val batch = builder.create(0, req)

      Utils.waitUntil({ () => !batch.state.isActive }, Duration(10, TimeUnit.SECONDS))
      (batch.state match {
        case SessionState.Success(_) => true
        case _ => false
      }) should be (true)

      batch.logLines() should contain("hello world")
    }
  }
}
