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

import com.cloudera.hue.livy.repl.python.PythonSession
import org.json4s.Extraction
import org.json4s.JsonAST.JValue

import _root_.scala.concurrent.Await
import _root_.scala.concurrent.duration.Duration

class PythonSessionSpec extends BaseSessionSpec {

  override def createSession() = PythonSession.create()

  describe("A python session") {
    it("should execute `1 + 2` == 3") {
      val statement = session.execute("1 + 2")
      statement.id should equal (0)

      val result = Await.result(statement.result, Duration.Inf)
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
      var statement = session.execute("x = 1")
      statement.id should equal (0)

      var result = Await.result(statement.result, Duration.Inf)
      var expectedResult = Extraction.decompose(Map(
        "status" -> "ok",
        "execution_count" -> 0,
        "data" -> Map(
          "text/plain" -> ""
        )
      ))

      result should equal (expectedResult)

      statement = session.execute("y = 2")
      statement.id should equal (1)

      result = Await.result(statement.result, Duration.Inf)
      expectedResult = Extraction.decompose(Map(
        "status" -> "ok",
        "execution_count" -> 1,
        "data" -> Map(
          "text/plain" -> ""
        )
      ))

      result should equal (expectedResult)

      statement = session.execute("x + y")
      statement.id should equal (2)

      result = Await.result(statement.result, Duration.Inf)
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
      val statement = session.execute("x = [[1, 'a'], [3, 'b']]\n%table x")
      statement.id should equal (0)

      val result = Await.result(statement.result, Duration.Inf)
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
      val statement = session.execute("""print 'Hello World'""")
      statement.id should equal (0)

      val result = Await.result(statement.result, Duration.Inf)
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
      val statement = session.execute("""x""")
      statement.id should equal (0)

      val result = Await.result(statement.result, Duration.Inf)
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
      val statement = session.execute(
        """def foo():
          |    raise Exception()
          |foo()
          |""".stripMargin)
      statement.id should equal (0)

      val result = Await.result(statement.result, Duration.Inf)
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
      val statement = session.execute("""sc""")
      statement.id should equal (0)

      val result = Await.result(statement.result, Duration.Inf)
      val resultMap = result.extract[Map[String, JValue]]

      // Manually extract the values since the line numbers in the exception could change.
      resultMap("status").extract[String] should equal ("ok")
      resultMap("execution_count").extract[Int] should equal (0)

      val data = resultMap("data").extract[Map[String, JValue]]
      data("text/plain").extract[String] should include ("<pyspark.context.SparkContext object at")
    }

    it("should execute spark commands") {
      val statement = session.execute("""
          |sc.parallelize(xrange(0, 2)).map(lambda i: i + 1).collect()
          |""".stripMargin)
      statement.id should equal (0)

      val result = Await.result(statement.result, Duration.Inf)

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
