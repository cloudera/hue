package com.cloudera.hue.livy.server.batches

import java.io.FileWriter
import java.nio.file.{Files, Path}

import com.cloudera.hue.livy.server.batch._
import org.json4s.JsonAST.{JArray, JInt, JObject, JString}
import org.json4s.jackson.JsonMethods._
import org.json4s.jackson.Serialization.write
import org.json4s.{DefaultFormats, Formats}
import org.scalatest.{BeforeAndAfter, BeforeAndAfterAll, FunSpecLike}
import org.scalatra.test.scalatest.ScalatraSuite

class BatchServletSpec extends ScalatraSuite with FunSpecLike with BeforeAndAfterAll with BeforeAndAfter {

  protected implicit def jsonFormats: Formats = DefaultFormats

  var script: Path = _

  val batchFactory = new BatchProcessFactory()
  val batchManager = new BatchManager(batchFactory)
  val servlet = new BatchServlet(batchManager)

  addServlet(servlet, "/*")

  override def beforeAll() = {
    super.beforeAll()
    script = Files.createTempFile("test", "livy-test")
    val writer = new FileWriter(script.toFile)
    try {
      writer.write("print 'hello world'")
    } finally {
      writer.close()
    }
  }

  override def afterAll() = {
    script.toFile.delete()
    super.afterAll()
  }

  after {
    batchManager.shutdown()
  }

  describe("Batch Servlet") {
    it("should create and tear down a batch") {
      get("/") {
        status should equal (200)
        header("Content-Type") should include("application/json")
        val parsedBody = parse(body)
        parsedBody \ "batches" should equal (JArray(List()))
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

        val batch = batchManager.getBatch(0)
        batch should be (defined)
      }

      delete("/0") {
        status should equal (200)
        header("Content-Type") should include("application/json")
        val parsedBody = parse(body)
        parsedBody should equal (JObject(("msg", JString("deleted"))))

        val batch = batchManager.getBatch(0)
        batch should not be defined
      }
    }
  }

}
