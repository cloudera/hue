package com.cloudera.hue.livy.server.batch

import com.cloudera.hue.livy.Logging
import com.fasterxml.jackson.core.JsonParseException
import org.json4s._
import org.scalatra._
import org.scalatra.json.JacksonJsonSupport

import scala.concurrent.{Future, ExecutionContext, ExecutionContextExecutor}

object BatchServlet extends Logging

class BatchServlet(batchManager: BatchManager)
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
      case Some(batch) =>
        val from = params.get("from").map(_.toInt)
        val size = params.get("size").map(_.toInt)

        Serializers.serializeBatch(batch, from, size)
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
      BatchServlet.error("internal error", e)
      InternalServerError(e.toString)
  }
}

private object Serializers {
  import JsonDSL._

  def Formats: List[CustomSerializer[_]] = List(BatchSerializer)

  def serializeBatch(batch: Batch,
                     fromOpt: Option[Int],
                     sizeOpt: Option[Int]): JValue = {
    val lines = batch.lines
    val size = sizeOpt.getOrElse(10)
    val from = fromOpt.getOrElse(math.max(0, lines.length - 10))
    val until = from + size

    ("id", batch.id) ~
      ("state", batch.state.toString) ~
      ("lines", lines.slice(from, until))
  }

  case object BatchSerializer extends CustomSerializer[Batch](
    implicit formats => ( {
    // We don't support deserialization.
    PartialFunction.empty
  }, {
    case batch: Batch =>
      serializeBatch(batch, None, None)
  }
    )
  )
}
