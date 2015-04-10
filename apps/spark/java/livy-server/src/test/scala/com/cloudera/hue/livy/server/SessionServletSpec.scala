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

package com.cloudera.hue.livy.server

import java.net.URL
import java.util.concurrent.atomic.AtomicInteger

import com.cloudera.hue.livy.msgs.ExecuteRequest
import com.cloudera.hue.livy.server.sessions._
import com.cloudera.hue.livy.sessions._
import org.json4s.JValue
import org.json4s.JsonAST.{JObject, JArray}
import org.json4s.jackson.JsonMethods._
import org.scalatest.FunSpecLike
import org.scalatra.test.scalatest.ScalatraSuite

import scala.collection.mutable.ArrayBuffer
import scala.concurrent.Future

class SessionServletSpec extends ScalatraSuite with FunSpecLike {

  class MockSession(val id: Int) extends Session {
    var _state: State = Idle()

    var _idCounter = new AtomicInteger()
    var _statements: ArrayBuffer[Statement] = ArrayBuffer()

    override def kind: Kind = Spark()

    override def state = _state

    override def stop(): Future[Unit] = ???

    override def url_=(url: URL): Unit = ???

    override def lastActivity: Long = ???

    override def executeStatement(executeRequest: ExecuteRequest): Statement = {
      val id = _idCounter.getAndIncrement
      val statement = new Statement(
        id,
        executeRequest,
        Future.successful(JObject()))

      _statements += statement

      statement
    }

    override def proxyUser: Option[String] = None

    override def url: Option[URL] = ???

    override def statement(statementId: Int): Option[Statement] = ???

    override def statements(): Seq[Statement] = _statements

    override def statements(fromIndex: Integer, toIndex: Integer): Seq[Statement] = ???

    override def interrupt(): Future[Unit] = ???
  }

  class MockSessionFactory() extends SessionFactory {
    override def createSession(id: Int, kind: Kind, proxyUser: Option[String]): Future[Session] = {
      Future.successful(new MockSession(id))
    }
  }

  val sessionManager = new SessionManager(new MockSessionFactory())
  val servlet = new SessionServlet(sessionManager)

  addServlet(servlet, "/*")

  describe("For /sessions") {
    it("GET / should return the sessions") {
      get("/") {
        status should equal (200)
        header("Content-Type") should include("application/json")
        val parsedBody = parse(body)
        parsedBody \ "sessions" should equal (JArray(List()))
      }
    }
  }

}
