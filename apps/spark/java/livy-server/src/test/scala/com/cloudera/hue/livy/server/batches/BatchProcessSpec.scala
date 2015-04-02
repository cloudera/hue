package com.cloudera.hue.livy.server.batches

import java.io.FileWriter
import java.nio.file.{Files, Path}
import java.util.concurrent.TimeUnit

import com.cloudera.hue.livy.Utils
import com.cloudera.hue.livy.server.batch.{Dead, CreateBatchRequest, BatchProcess}
import org.scalatest.{ShouldMatchers, BeforeAndAfterAll, FunSpec}

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
      val batch = BatchProcess(0, "local[*]", req)

      Utils.waitUntil({ () =>
        batch.state == Dead()
      }, Duration(10, TimeUnit.SECONDS))

      batch.lines should contain("hello world")
    }
  }
}
