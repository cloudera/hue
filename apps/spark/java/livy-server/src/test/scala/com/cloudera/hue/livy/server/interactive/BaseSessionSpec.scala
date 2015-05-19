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

package com.cloudera.hue.livy.server.interactive

import java.util.concurrent.TimeUnit

import com.cloudera.hue.livy.msgs.ExecuteRequest
import com.cloudera.hue.livy.sessions.{Idle, Starting}
import org.json4s.{DefaultFormats, Extraction}
import org.scalatest.{BeforeAndAfter, FunSpec, Matchers}

import scala.concurrent.Await
import scala.concurrent.duration.Duration

abstract class BaseSessionSpec extends FunSpec with Matchers with BeforeAndAfter {

  implicit val formats = DefaultFormats

  var session: InteractiveSession = null

  def createSession(): InteractiveSession

  before {
    session = createSession()
  }

  after {
    session.stop()
  }

  describe("A spark session") {
    it("should start in the starting or idle state") {
      session.state should (equal (Starting()) or equal (Idle()))
    }

    it("should eventually become the idle state") {
      session.waitForStateChange(Starting(), Duration(30, TimeUnit.SECONDS))
      session.state should equal (Idle())
    }

    it("should execute `1 + 2` == 3") {
      session.waitForStateChange(Starting(), Duration(30, TimeUnit.SECONDS))
      val stmt = session.executeStatement(ExecuteRequest("1 + 2"))
      val result = Await.result(stmt.output(), Duration.Inf)

      val expectedResult = Extraction.decompose(Map(
        "status" -> "ok",
        "execution_count" -> 0,
        "data" -> Map(
          "text/plain" -> "res0: Int = 3"
        )
      ))

      result should equal (expectedResult)
    }

    it("should report an error if accessing an unknown variable") {
      session.waitForStateChange(Starting(), Duration(30, TimeUnit.SECONDS))
      val stmt = session.executeStatement(ExecuteRequest("x"))
      val result = Await.result(stmt.output(), Duration.Inf)
      val expectedResult = Extraction.decompose(Map(
        "status" -> "error",
        "execution_count" -> 0,
        "ename" -> "Error",
        "evalue" ->
          """<console>:8: error: not found: value x
            |              x
            |              ^""".stripMargin
      ))

      result should equal (expectedResult)
    }
  }
}
