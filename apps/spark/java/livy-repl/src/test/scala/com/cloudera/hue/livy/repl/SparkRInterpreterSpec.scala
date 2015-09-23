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

import com.cloudera.hue.livy.repl
import com.cloudera.hue.livy.repl.sparkr.SparkRInterpreter
import org.json4s.JsonDSL._
import org.json4s.{DefaultFormats, JValue}

class SparkRInterpreterSpec extends BaseInterpreterSpec {

  implicit val formats = DefaultFormats

  override protected def withFixture(test: NoArgTest) = {
    val sparkRExecutable = SparkRInterpreter.sparkRExecutable
    assume(sparkRExecutable.isDefined, "Cannot find sparkR")
    test()
  }

  override def createInterpreter() = {
    SparkRInterpreter()
  }

  it should "execute `1 + 2` == 3" in withInterpreter { interpreter =>
    val response = interpreter.execute("1 + 2")
    response should equal (Interpreter.ExecuteSuccess(
      repl.TEXT_PLAIN -> "[1] 3"
    ))
  }

  it should "execute multiple statements" in withInterpreter { interpreter =>
    var response = interpreter.execute("x = 1")
    response should equal (Interpreter.ExecuteSuccess(
      repl.TEXT_PLAIN -> ""
    ))

    response = interpreter.execute("y = 2")
    response should equal (Interpreter.ExecuteSuccess(
      repl.TEXT_PLAIN -> ""
    ))

    response = interpreter.execute("x + y")
    response should equal (Interpreter.ExecuteSuccess(
      repl.TEXT_PLAIN -> "[1] 3"
    ))
  }

  it should "execute multiple statements in one block" in withInterpreter { interpreter =>
    val response = interpreter.execute(
      """
        |x = 1
        |
        |y = 2
        |
        |x + y
      """.stripMargin)
    response should equal(Interpreter.ExecuteSuccess(
      repl.TEXT_PLAIN -> "[1] 3"
    ))
  }

  it should "capture stdout" in withInterpreter { interpreter =>
    val response = interpreter.execute("cat(3)")
    response should equal(Interpreter.ExecuteSuccess(
      repl.TEXT_PLAIN -> "3"
    ))
  }

  it should "report an error if accessing an unknown variable" in withInterpreter { interpreter =>
    val response = interpreter.execute("x")
    response should equal(Interpreter.ExecuteSuccess(
      repl.TEXT_PLAIN -> "Error: object 'x' not found"
    ))
  }

  it should "execute spark commands" in withInterpreter { interpreter =>
    val response = interpreter.execute(
      """head(createDataFrame(sqlContext, faithful))""")

    response match {
      case Interpreter.ExecuteSuccess(map: JValue) =>
        (map \ "text/plain").extract[String] should include (
          """  eruptions waiting
            |1     3.600      79
            |2     1.800      54
            |3     3.333      74
            |4     2.283      62
            |5     4.533      85
            |6     2.883      55""".stripMargin)
      case _ =>
        throw new Exception("response is not a success")
    }

  }
}
