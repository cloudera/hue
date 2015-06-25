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

package com.cloudera.hue.livy.server.batches

import java.io.FileWriter
import java.nio.file.{Files, Path}
import java.util.concurrent.TimeUnit

import com.cloudera.hue.livy.server.SessionManager
import com.cloudera.hue.livy.sessions.Success
import com.cloudera.hue.livy.{LivyConf, Utils}
import com.cloudera.hue.livy.server.batch._
import org.json4s.JsonAST.{JArray, JInt, JObject, JString}
import org.json4s.jackson.JsonMethods._
import org.json4s.jackson.Serialization.write
import org.json4s.{DefaultFormats, Formats}
import org.scalatest.{BeforeAndAfter, BeforeAndAfterAll, FunSpecLike}
import org.scalatra.test.scalatest.ScalatraSuite

import scala.concurrent.duration.Duration

class BatchServletSpec extends ScalatraSuite with FunSpecLike with BeforeAndAfterAll with BeforeAndAfter {

  protected implicit def jsonFormats: Formats = DefaultFormats

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

  val batchFactory = new BatchSessionProcessFactory(new LivyConf())
  val batchManager = new SessionManager(batchFactory)
  val servlet = new BatchSessionServlet(batchManager)

  addServlet(servlet, "/*")

  after {
    batchManager.shutdown()
  }

  describe("Batch Servlet") {
    it("should create and tear down a batch") {
      get("/") {
        status should equal (200)
        header("Content-Type") should include("application/json")
        val parsedBody = parse(body)
        parsedBody \ "sessions" should equal (JArray(List()))
      }

      val createBatchRequest = write(CreateBatchRequest(
        file = script.toString
      ))

      post("/", body = createBatchRequest, headers = Map("Content-Type" -> "application/json")) {
        status should equal (201)
        header("Content-Type") should include("application/json")
        header("Location") should equal("/0")
        val parsedBody = parse(body)
        parsedBody \ "id" should equal (JInt(0))

        val batch = batchManager.get(0)
        batch should be (defined)
      }

      // Wait for the process to finish.
      {
        val batch: BatchSession = batchManager.get(0).get
        Utils.waitUntil({ () =>
          batch.state == Success()
        }, Duration(10, TimeUnit.SECONDS))
      }

      get("/0") {
        status should equal (200)
        header("Content-Type") should include("application/json")
        val parsedBody = parse(body)
        parsedBody \ "id" should equal (JInt(0))
        parsedBody \ "state" should equal (JString("success"))

        val batch = batchManager.get(0)
        batch should be (defined)
      }

      get("/0/log?size=1000") {
        status should equal (200)
        header("Content-Type") should include("application/json")
        val parsedBody = parse(body)
        parsedBody \ "id" should equal (JInt(0))
        (parsedBody \ "log").extract[List[String]] should contain ("hello world")

        val batch = batchManager.get(0)
        batch should be (defined)
      }

      delete("/0") {
        status should equal (200)
        header("Content-Type") should include("application/json")
        val parsedBody = parse(body)
        parsedBody should equal (JObject(("msg", JString("deleted"))))

        val batch = batchManager.get(0)
        batch should not be defined
      }
    }
  }

}
