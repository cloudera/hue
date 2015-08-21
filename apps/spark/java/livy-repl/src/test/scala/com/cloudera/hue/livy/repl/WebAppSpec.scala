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

package com.cloudera.hue.livy.repl

import java.util.concurrent.TimeUnit

import com.cloudera.hue.livy.repl
import com.cloudera.hue.livy.sessions._
import org.json4s.JsonAST.{JArray, JString}
import org.json4s.JsonDSL._
import org.json4s.jackson.JsonMethods._
import org.json4s.{JValue, DefaultFormats, Extraction}
import org.scalatest.{BeforeAndAfter, FunSpecLike}
import org.scalatra.test.scalatest.ScalatraSuite

import _root_.scala.concurrent.duration.Duration
import _root_.scala.concurrent.{Await, Future}

class WebAppSpec extends ScalatraSuite with FunSpecLike with BeforeAndAfter {

  implicit val formats = DefaultFormats

  class MockInterpreter extends Interpreter {
    override def kind: String = "mock"

    override def start() = {}

    override def execute(code: String) = {
      Thread.sleep(1000)
      Interpreter.ExecuteSuccess(repl.TEXT_PLAIN -> "1")
    }

    override def close() = {}
  }

  val interpreter = new MockInterpreter()
  val session = new Session(new MockInterpreter())

  val servlet = new WebApp(session)

  addServlet(servlet, "/*")

  describe("A session") {
    it("GET / should return the session state") {
      get("/") {
        status should equal (200)
        header("Content-Type") should include("application/json")
        val parsedBody = parse(body)
        parsedBody \ "state" should equal (JString("idle"))
      }

      session.execute("")

      get("/") {
        status should equal (200)
        header("Content-Type") should include("application/json")
        val parsedBody = parse(body)
        parsedBody \ "state" should equal (JString("busy"))
      }
    }

    it("GET /history with no history should be empty") {
      get("/history") {
        status should equal (200)
        header("Content-Type") should include("application/json")
        parse(body) should equal (
          ("from", 0) ~
            ("total", 0) ~
            ("statements", JArray(List())))
      }
    }

    it("GET /history with history should return something") {
      Await.ready(session.execute("").result, Duration(10, TimeUnit.SECONDS))

      get("/history") {
        status should equal (200)
        header("Content-Type") should include("application/json")
        parse(body) should equal (
          ("from" -> 0) ~
          ("total" -> 1) ~
          (
            "statements" -> List[JValue](
              ("id" -> 0) ~
              ("result" ->
                ("status" -> "ok") ~
                ("execution_count" -> 0) ~
                ("data" -> (repl.TEXT_PLAIN -> "1"))
              )
            )
          )
        )
      }
    }

    after {
      session.clearHistory()
    }
  }
}
