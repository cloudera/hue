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

package com.cloudera.hue.livy.server.batch

import com.cloudera.hue.livy.Logging
import com.fasterxml.jackson.core.JsonParseException
import org.json4s.JsonDSL._
import org.json4s._
import org.scalatra._
import org.scalatra.json.JacksonJsonSupport

import scala.concurrent.{Future, ExecutionContext, ExecutionContextExecutor}

object BatchSessionServlet extends Logging

class BatchSessionServlet(batchManager: BatchManager)
  extends ScalatraServlet
  with FutureSupport
  with MethodOverride
  with JacksonJsonSupport
  with UrlGeneratorSupport
{
  override protected implicit def executor: ExecutionContextExecutor = ExecutionContext.global
  override protected implicit def jsonFormats: Formats = DefaultFormats ++ Serializers.Formats

  before() {
    contentType = formats("json")
  }

  get("/") {
    Map(
      "batches" -> batchManager.getBatches
    )
  }

  post("/") {
    val createBatchRequest = parsedBody.extract[CreateBatchRequest]

    new AsyncResult {
      val is = Future {
        val batch = batchManager.createBatch(createBatchRequest)
        Created(batch,
          headers = Map(
            "Location" -> url(getBatch, "id" -> batch.id.toString)
          )
        )
      }
    }
  }

  val getBatch = get("/:id") {
    val id = params("id").toInt

    batchManager.getBatch(id) match {
      case None => NotFound("batch not found")
      case Some(batch) => Serializers.serializeBatch(batch)
    }
  }

  get("/:id/state") {
    val id = params("id").toInt

    batchManager.getBatch(id) match {
      case None => NotFound("batch not found")
      case Some(batch) =>
        ("id", batch.id) ~ ("state", batch.state.toString)
    }
  }

  get("/:id/log") {
    val id = params("id").toInt

    batchManager.getBatch(id) match {
      case None => NotFound("batch not found")
      case Some(batch) =>
        val from = params.get("from").map(_.toInt)
        val size = params.get("size").map(_.toInt)
        val (from_, total, logLines) = Serializers.getLogs(batch, from, size)

        ("id", batch.id) ~
          ("from", from_) ~
          ("total", total) ~
          ("log", logLines)
    }
  }

  delete("/:id") {
    val id = params("id").toInt

    batchManager.remove(id) match {
      case None => NotFound("batch not found")
      case Some(batch) =>
        new AsyncResult {
          val is = batch.stop().map { case () =>
            batchManager.delete(batch)
            Ok(Map("msg" -> "deleted"))
          }
        }
    }
  }

  error {
    case e: JsonParseException => BadRequest(e.getMessage)
    case e: MappingException => BadRequest(e.getMessage)
    case e =>
      BatchSessionServlet.error("internal error", e)
      InternalServerError(e.toString)
  }
}

private object Serializers {
  import org.json4s.JsonDSL._

  def Formats: List[CustomSerializer[_]] = List(BatchSerializer)

  def serializeBatch(batch: BatchSession): JValue = {
    ("id", batch.id) ~
      ("state", batch.state.toString) ~
      ("log", getLogs(batch, None, Some(10))._3)
  }

  def getLogs(batch: BatchSession, fromOpt: Option[Int], sizeOpt: Option[Int]) = {
    val lines = batch.logLines()

    val size = sizeOpt.getOrElse(100)
    var from = fromOpt.getOrElse(-1)
    if (from < 0) {
      from = math.max(0, lines.length - size)
    }
    val until = from + size

    (from, lines.length, lines.view(from, until))
  }

  case object BatchSerializer extends CustomSerializer[BatchSession](
    implicit formats => ( {
    // We don't support deserialization.
    PartialFunction.empty
  }, {
    case batch: BatchSession => serializeBatch(batch)
  }
    )
  )
}
