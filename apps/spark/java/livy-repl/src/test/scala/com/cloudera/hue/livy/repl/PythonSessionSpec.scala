package com.cloudera.hue.livy.repl

import com.cloudera.hue.livy.repl.python.PythonSession
import org.json4s.JsonAST.JValue
import org.json4s.{Extraction, DefaultFormats}
import org.scalatest.{BeforeAndAfter, FunSpec}
import org.scalatest.matchers.ShouldMatchers

import _root_.scala.concurrent.Await
import _root_.scala.concurrent.duration.Duration

class PythonSessionSpec extends FunSpec with ShouldMatchers with BeforeAndAfter {

  implicit val formats = DefaultFormats

  var session: Session = null

  before {
    session = PythonSession.createPython()
  }

  after {
    session.close()
  }

  describe("A python session") {
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
          "text/plain" -> "3"
        )
      ))

      result should equal (expectedResult)
    }

    it("should execute `x = 1`, then `y = 2`, then `x + y`") {
      var result = Await.result(session.execute("x = 1"), Duration.Inf)
      var expectedResult = Extraction.decompose(Map(
        "status" -> "ok",
        "execution_count" -> 0,
        "data" -> Map(
          "text/plain" -> ""
        )
      ))

      result should equal (expectedResult)

      result = Await.result(session.execute("y = 2"), Duration.Inf)
      expectedResult = Extraction.decompose(Map(
        "status" -> "ok",
        "execution_count" -> 1,
        "data" -> Map(
          "text/plain" -> ""
        )
      ))

      result should equal (expectedResult)

      result = Await.result(session.execute("x + y"), Duration.Inf)
      expectedResult = Extraction.decompose(Map(
        "status" -> "ok",
        "execution_count" -> 2,
        "data" -> Map(
          "text/plain" -> "3"
        )
      ))

      result should equal (expectedResult)
    }

    it("should do table magic") {
      val result = Await.result(session.execute("x = [[1, 'a'], [3, 'b']]\n%table x"), Duration.Inf)
      val expectedResult = Extraction.decompose(Map(
        "status" -> "ok",
        "execution_count" -> 1,
        "data" -> Map(
          "application/vnd.livy.table.v1+json" -> Map(
            "headers" -> List(
              Map("type" -> "INT_TYPE", "name" -> "0"),
              Map("type" -> "STRING_TYPE", "name" -> "1")),
            "data" -> List(List(1, "a"), List(3, "b"))
          )
        )
      ))

      result should equal (expectedResult)
    }

    it("should capture stdout") {
      val result = Await.result(session.execute("""print 'Hello World'"""), Duration.Inf)
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
        "traceback" -> List(
          "Traceback (most recent call last):\n",
          "NameError: name 'x' is not defined\n"
        ),
        "ename" -> "NameError",
        "evalue" -> "name 'x' is not defined"
      ))

      result should equal (expectedResult)
    }

    it("should report an error if exception is thrown") {
      val result = Await.result(session.execute(
        """def foo():
          |    raise Exception()
          |foo()
          |""".stripMargin), Duration.Inf)
      val expectedResult = Extraction.decompose(Map(
        "status" -> "error",
        "execution_count" -> 0,
        "traceback" -> List(
          "Traceback (most recent call last):\n",
          "Exception\n"
        ),
        "ename" -> "Exception",
        "evalue" -> ""
      ))

      result should equal (expectedResult)
    }

    it("should access the spark context") {
      val result = Await.result(session.execute("""sc"""), Duration.Inf)
      val resultMap = result.extract[Map[String, JValue]]

      // Manually extract the values since the line numbers in the exception could change.
      resultMap("status").extract[String] should equal ("ok")
      resultMap("execution_count").extract[Int] should equal (0)

      val data = resultMap("data").extract[Map[String, JValue]]
      data("text/plain").extract[String] should include ("<pyspark.context.SparkContext object at")
    }

    it("should execute spark commands") {
      val result = Await.result(session.execute(
        """
          |sc.parallelize(xrange(0, 2)).map(lambda i: i + 1).collect()
          |""".stripMargin), Duration.Inf)

      val expectedResult = Extraction.decompose(Map(
        "status" -> "ok",
        "execution_count" -> 0,
        "data" -> Map(
          "text/plain" -> "[1, 2]"
        )
      ))

      result should equal (expectedResult)
    }
  }
}
