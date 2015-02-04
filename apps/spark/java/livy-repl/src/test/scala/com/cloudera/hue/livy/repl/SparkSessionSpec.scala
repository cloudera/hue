package com.cloudera.hue.livy.repl

import com.cloudera.hue.livy.repl.scala.SparkSession
import org.json4s.{Extraction, DefaultFormats}
import org.scalatest.{BeforeAndAfter, FunSpec}
import org.scalatest.matchers.ShouldMatchers

import _root_.scala.concurrent.Await
import _root_.scala.concurrent.duration.Duration

class SparkSessionSpec extends FunSpec with ShouldMatchers with BeforeAndAfter {

  implicit val formats = DefaultFormats

  var session: Session = null

  before {
    session = SparkSession.create()
  }

  after {
    session.close()
  }

  describe("A spark session") {
    it("should start in the starting or idle state") {
      session.state should (equal (Session.Starting()) or equal (Session.Idle()))
    }

    it("should eventually become the idle state") {
      session.waitForStateChange(Session.Starting())
      session.state should equal (Session.Idle())
    }

    it("should execute `1 + 2` == 3") {
      val result = Await.result(session.execute("1 + 2"), Duration.Inf)
      val expectedResult = Extraction.decompose(Map(
        "status" -> "ok",
        "execution_count" -> 0,
        "data" -> Map(
          "text/plain" -> "res0: Int = 3"
        )
      ))

      result should equal (expectedResult)
    }

    it("should execute `x = 1`, then `y = 2`, then `x + y`") {
      var result = Await.result(session.execute("val x = 1"), Duration.Inf)
      var expectedResult = Extraction.decompose(Map(
        "status" -> "ok",
        "execution_count" -> 0,
        "data" -> Map(
          "text/plain" -> "x: Int = 1"
        )
      ))

      result should equal (expectedResult)

      result = Await.result(session.execute("val y = 2"), Duration.Inf)
      expectedResult = Extraction.decompose(Map(
        "status" -> "ok",
        "execution_count" -> 1,
        "data" -> Map(
          "text/plain" -> "y: Int = 2"
        )
      ))

      result should equal (expectedResult)

      result = Await.result(session.execute("x + y"), Duration.Inf)
      expectedResult = Extraction.decompose(Map(
        "status" -> "ok",
        "execution_count" -> 2,
        "data" -> Map(
          "text/plain" -> "res0: Int = 3"
        )
      ))

      result should equal (expectedResult)
    }
  }
 }
