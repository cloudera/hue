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

import com.cloudera.hue.livy.Logging
import com.cloudera.hue.livy.msgs.ExecuteRequest
import com.cloudera.hue.livy.sessions._
import com.fasterxml.jackson.core.JsonParseException
import org.json4s.{DefaultFormats, MappingException}
import org.scalatra._
import org.scalatra.json.JacksonJsonSupport

import _root_.scala.concurrent.{Future, ExecutionContext}

object WebApp extends Logging

class WebApp(session: Session) extends ScalatraServlet with FutureSupport with JacksonJsonSupport {

  override protected implicit def executor: ExecutionContext = ExecutionContext.global
  override protected implicit val jsonFormats = DefaultFormats

  before() {
    contentType = formats("json")

    session.state match {
      case ShuttingDown() => halt(500, "Shutting down")
      case _ => {}
    }
  }

  get("/") {
    val state = session.state match {
      case NotStarted() => "not_started"
      case Starting() => "starting"
      case Idle() => "idle"
      case Busy() => "busy"
      case Error() => "error"
      case ShuttingDown() => "shutting_down"
      case Dead() => "dead"
    }
    Map("state" -> state)
  }

  post("/execute") {
    val req = parsedBody.extract[ExecuteRequest]
    val rep = session.execute(req.code)
    new AsyncResult { val is = rep }
  }

  get("/history") {
    session.history()
  }

  get("/history/:statementId") {
    val statementId = params("statementId").toInt

    session.history(statementId) match {
      case Some(statement) => statement
      case None => NotFound("Statement not found")
    }
  }

  delete("/") {
    session.close()
    Future {
      Thread.sleep(1000)
      System.exit(0)
    }
  }

  error {
    case e: JsonParseException => BadRequest(e.getMessage)
    case e: MappingException => BadRequest(e.getMessage)
    case e =>
      WebApp.error("internal error", e)
      InternalServerError(e.toString)
  }
}

