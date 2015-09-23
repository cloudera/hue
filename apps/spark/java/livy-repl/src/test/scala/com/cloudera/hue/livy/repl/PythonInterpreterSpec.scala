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
import com.cloudera.hue.livy.repl.python.PythonInterpreter
import org.json4s.JsonDSL._
import org.json4s.{DefaultFormats, JValue}

class PythonInterpreterSpec extends BaseInterpreterSpec {

  implicit val formats = DefaultFormats

  override def createInterpreter() = PythonInterpreter()

  it should "execute `1 + 2` == 3" in withInterpreter { interpreter =>
    val response = interpreter.execute("1 + 2")
    response should equal (Interpreter.ExecuteSuccess(
      repl.TEXT_PLAIN -> "3"
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
      repl.TEXT_PLAIN -> "3"
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
      repl.TEXT_PLAIN -> "3"
    ))
  }

  it should "do table magic" in withInterpreter { interpreter =>
    val response = interpreter.execute(
      """x = [[1, 'a'], [3, 'b']]
        |%table x
      """.stripMargin)

    response should equal(Interpreter.ExecuteSuccess(
      repl.APPLICATION_LIVY_TABLE_JSON -> (
        ("headers" -> List(
          ("type" -> "INT_TYPE") ~ ("name" -> "0"),
          ("type" -> "STRING_TYPE") ~ ("name" -> "1")
        )) ~
          ("data" -> List(
            List[JValue](1, "a"),
            List[JValue](3, "b")
          ))
        )
    ))
  }

  it should "allow magic inside statements" in withInterpreter { interpreter =>
    val response = interpreter.execute(
      """x = [[1, 'a'], [3, 'b']]
        |%table x
        |1 + 2
      """.stripMargin)

    response should equal(Interpreter.ExecuteSuccess(
      repl.TEXT_PLAIN -> "3"
    ))
  }

  it should "capture stdout" in withInterpreter { interpreter =>
    val response = interpreter.execute("print 'Hello World'")
    response should equal(Interpreter.ExecuteSuccess(
      repl.TEXT_PLAIN -> "Hello World"
    ))
  }

  it should "report an error if accessing an unknown variable" in withInterpreter { interpreter =>
    val response = interpreter.execute("x")
    response should equal(Interpreter.ExecuteError(
      "NameError",
      "name 'x' is not defined",
      List(
        "Traceback (most recent call last):\n",
        "NameError: name 'x' is not defined\n"
      )
    ))
  }

  it should "execute spark commands" in withInterpreter { interpreter =>
    val response = interpreter.execute(
      """sc.parallelize(xrange(0, 2)).map(lambda i: i + 1).collect()""")

    response should equal(Interpreter.ExecuteSuccess(
      repl.TEXT_PLAIN -> "[1, 2]"
    ))
  }
}
