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

import com.cloudera.hue.livy.repl.sparkr.SparkRInterpreter
import org.json4s.Extraction
import org.json4s.JsonAST.JValue
import org.scalatest.BeforeAndAfterAll

import _root_.scala.concurrent.Await
import _root_.scala.concurrent.duration.Duration

class SparkRSessionSpec extends BaseSessionSpec {

  override protected def withFixture(test: NoArgTest) = {
    val sparkRExecutable = SparkRInterpreter.sparkRExecutable
    assume(sparkRExecutable.isDefined, "Cannot find sparkR")
    test()
  }

  override def createInterpreter() = SparkRInterpreter()

  it should "execute `1 + 2` == 3" in withSession { session =>
    val statement = session.execute("1 + 2")
    statement.id should equal(0)

    val result = Await.result(statement.result, Duration.Inf)
    val expectedResult = Extraction.decompose(Map(
      "status" -> "ok",
      "execution_count" -> 0,
      "data" -> Map(
        "text/plain" -> "[1] 3"
      )
    ))

    result should equal(expectedResult)
  }

    it should "execute `x = 1`, then `y = 2`, then `x + y`" in withSession { session =>
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
        "text/plain" -> "[1] 3"
      )
    ))

    result should equal (expectedResult)
  }

    it should "capture stdout from print" in withSession { session =>
    val statement = session.execute("""print('Hello World')""")
    statement.id should equal (0)

    val result = Await.result(statement.result, Duration.Inf)
    val expectedResult = Extraction.decompose(Map(
      "status" -> "ok",
      "execution_count" -> 0,
      "data" -> Map(
        "text/plain" -> "[1] \"Hello World\""
      )
    ))

    result should equal (expectedResult)
  }

    it should "capture stdout from cat" in withSession { session =>
    val statement = session.execute("""cat(3)""")
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

    it should "report an error if accessing an unknown variable" in withSession { session =>
    val statement = session.execute("""x""")
    statement.id should equal (0)

    val result = Await.result(statement.result, Duration.Inf)
    val expectedResult = Extraction.decompose(Map(
      "status" -> "ok",
      "execution_count" -> 0,
      "data" -> Map(
        "text/plain" -> "Error: object 'x' not found"
      )
    ))

    result should equal (expectedResult)
  }

    it should "access the spark context" in withSession { session =>
    val statement = session.execute("""sc""")
    statement.id should equal (0)

    val result = Await.result(statement.result, Duration.Inf)
    val resultMap = result.extract[Map[String, JValue]]

    val expectedResult = Extraction.decompose(Map(
      "status" -> "ok",
      "execution_count" -> 0,
      "data" -> Map(
        "text/plain" -> "Java ref type org.apache.spark.api.java.JavaSparkContext id 0"
      )
    ))
  }

    it should "execute spark commands" in withSession { session =>
    val statement = session.execute("""
                                      |head(createDataFrame(sqlContext, faithful))
                                      |""".stripMargin)
    statement.id should equal (0)

    val result = Await.result(statement.result, Duration.Inf)
    val resultMap = result.extract[Map[String, JValue]]

    // Manually extract since sparkr outputs a lot of spark logging information.
    resultMap("status").extract[String] should equal ("ok")
    resultMap("execution_count").extract[Int] should equal (0)

    val data = resultMap("data").extract[Map[String, JValue]]
    data("text/plain").extract[String] should include ("""  eruptions waiting
                                                         |1     3.600      79
                                                         |2     1.800      54
                                                         |3     3.333      74
                                                         |4     2.283      62
                                                         |5     4.533      85
                                                         |6     2.883      55""".stripMargin)
  }
}
