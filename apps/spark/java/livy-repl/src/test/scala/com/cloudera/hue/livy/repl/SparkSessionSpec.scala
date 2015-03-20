package com.cloudera.hue.livy.repl

import com.cloudera.hue.livy.repl.scala.SparkSession
import org.json4s.JsonAST.JValue
import org.json4s.{DefaultFormats, Extraction}
import org.scalatest.matchers.ShouldMatchers
import org.scalatest.{BeforeAndAfter, FunSpec}

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

    it("should capture stdout") {
      val result = Await.result(session.execute("""println("Hello World")"""), Duration.Inf)
      val expectedResult = Extraction.decompose(Map(
        "status" -> "ok",
        "execution_count" -> 0,
        "data" -> Map(
          "text/plain" -> "Hello World"
        )
      ))

      result should equal (expectedResult)
    }

    it("should report an error if accessing an unknown variable") {
      val result = Await.result(session.execute("""x"""), Duration.Inf)
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

    it("should report an error if exception is thrown") {
      val result = Await.result(session.execute("""throw new Exception()"""), Duration.Inf)
      val resultMap = result.extract[Map[String, JValue]]

      // Manually extract the values since the line numbers in the exception could change.
      resultMap("status").extract[String] should equal ("error")
      resultMap("execution_count").extract[Int] should equal (0)
      resultMap("ename").extract[String] should equal ("Error")
      resultMap("evalue").extract[String] should include ("java.lang.Exception")
      resultMap.get("traceback") should equal (None)
    }

    it("should access the spark context") {
      val result = Await.result(session.execute("""sc"""), Duration.Inf)
      val resultMap = result.extract[Map[String, JValue]]

      // Manually extract the values since the line numbers in the exception could change.
      resultMap("status").extract[String] should equal ("ok")
      resultMap("execution_count").extract[Int] should equal (0)

      val data = resultMap("data").extract[Map[String, JValue]]
      data("text/plain").extract[String] should include ("res0: org.apache.spark.SparkContext = org.apache.spark.SparkContext")
    }

    it("should execute spark commands") {
      val result = Await.result(session.execute(
        """
          |sc.parallelize(0 to 1).map{i => i+1}.collect
          |""".stripMargin), Duration.Inf)

      val expectedResult = Extraction.decompose(Map(
        "status" -> "ok",
        "execution_count" -> 0,
        "data" -> Map(
          "text/plain" -> "res0: Array[Int] = Array(1, 2)"
        )
      ))

      result should equal (expectedResult)
    }
  }
 }
