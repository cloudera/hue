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

import com.cloudera.hue.livy.sessions._
import org.json4s.JsonAST.{JArray, JString}
import org.json4s.JsonDSL._
import org.json4s.jackson.JsonMethods._
import org.json4s.{DefaultFormats, Extraction}
import org.scalatest.{BeforeAndAfter, FunSpecLike}
import org.scalatra.test.scalatest.ScalatraSuite

import _root_.scala.concurrent.Future

class WebAppSpec extends ScalatraSuite with FunSpecLike with BeforeAndAfter {

  implicit val formats = DefaultFormats

  class MockSession extends Session {
    var _state: State = Idle()
    var _history = IndexedSeq[Statement]()

    override def kind: Kind = Spark()

    override def state = _state

    override def execute(code: String): Statement = {
      val rep = render(Map("hi" -> "there"))
      val statement = Statement(0, Future.successful(rep))
      _history :+= statement
      statement
    }

    override def close(): Unit = {
      _state = Dead()
    }

    override def history: IndexedSeq[Statement] = _history
  }

  val session = new MockSession
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

      session._state = Busy()

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
      val history = Extraction.decompose(Map(
          "data" -> Map("text/plain" -> "1")
      ))
      session._history = IndexedSeq(Statement(0, Future.successful(history)))

      get("/history") {
        status should equal (200)
        header("Content-Type") should include("application/json")
        parse(body) should equal (
          ("from", 0) ~
            ("total", 1) ~
            ("statements", JArray(List( ("id", 0) ~ ("result", history)))))
      }
    }
  }

  after {
    session._state = Idle()
    session._history = IndexedSeq()
  }
}
