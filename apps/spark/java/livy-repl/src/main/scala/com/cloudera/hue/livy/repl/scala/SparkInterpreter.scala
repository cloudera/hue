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

package com.cloudera.hue.livy.repl.scala

import java.io._

import com.cloudera.hue.livy.repl
import com.cloudera.hue.livy.repl.Interpreter
import org.apache.spark.rdd.RDD
import org.apache.spark.repl.SparkIMain
import org.apache.spark.{SparkConf, SparkContext}
import org.json4s.JsonAST._
import org.json4s.JsonDSL._
import org.json4s.{DefaultFormats, Extraction}

import scala.tools.nsc.Settings
import scala.tools.nsc.interpreter.{JPrintWriter, Results}


object SparkInterpreter {
  private val MAGIC_REGEX = "^%(\\w+)\\W*(.*)".r

  def apply(): SparkInterpreter = { new SparkInterpreter }
}

/**
 * This represents a Spark interpreter. It is not thread safe.
 */
class SparkInterpreter extends Interpreter {
  import SparkInterpreter._

  private implicit def formats = DefaultFormats

  private val outputStream = new ByteArrayOutputStream()
  private var sparkIMain: SparkIMain = _
  private var sparkContext: SparkContext = _

  def kind = "spark"

  override def start() = {
    require(sparkIMain == null && sparkContext == null)

    val settings = new Settings()
    settings.usejavacp.value = true

    sparkIMain = new SparkIMain(settings, new JPrintWriter(outputStream, true))
    sparkIMain.initializeSynchronous()

    val sparkConf = new SparkConf(true)
      .setAppName("Livy Spark shell")
      .set("spark.repl.class.uri", sparkIMain.classServerUri)

    sparkContext = SparkContext.getOrCreate(sparkConf)

    sparkIMain.beQuietDuring {
      sparkIMain.bind("sc", "org.apache.spark.SparkContext", sparkContext, List("""@transient"""))
    }
  }

  override def execute(code: String): Interpreter.ExecuteResponse = {
    require(sparkIMain != null && sparkContext != null)

    executeLines(code.trim.split("\n").toList, Interpreter.ExecuteSuccess(JObject(
      (repl.TEXT_PLAIN, JString(""))
    )))
  }

  override def close(): Unit = synchronized {
    if (sparkContext != null) {
      sparkContext.stop()
    }

    if (sparkIMain != null) {
      sparkIMain.close()
      sparkIMain = null
    }
  }

  private def executeMagic(magic: String, rest: String): Interpreter.ExecuteResponse = {
    magic match {
      case "json" => executeJsonMagic(rest)
      case "table" => executeTableMagic(rest)
      case _ =>
        Interpreter.ExecuteError("UnknownMagic", f"Unknown magic command $magic")
    }
  }

  private def executeJsonMagic(name: String): Interpreter.ExecuteResponse = {
    try {
      val value = sparkIMain.valueOfTerm(name) match {
        case Some(obj: RDD[_]) => obj.asInstanceOf[RDD[_]].take(10)
        case Some(obj) => obj
        case None => return Interpreter.ExecuteError("NameError", f"Value $name does not exist")
      }

      Interpreter.ExecuteSuccess(JObject(
        (repl.APPLICATION_JSON, Extraction.decompose(value))
      ))
    } catch {
      case _: Throwable =>
        Interpreter.ExecuteError("ValueError", "Failed to convert value into a JSON value")
    }
  }

  private class TypesDoNotMatch extends Exception

  private def convertTableType(value: JValue): String = {
    value match {
      case (JNothing | JNull) => "NULL_TYPE"
      case JBool(_) => "BOOLEAN_TYPE"
      case JString(_) => "STRING_TYPE"
      case JInt(_) => "BIGINT_TYPE"
      case JDouble(_) => "DOUBLE_TYPE"
      case JDecimal(_) => "DECIMAL_TYPE"
      case JArray(arr) =>
        if (allSameType(arr.iterator)) {
          "ARRAY_TYPE"
        } else {
          throw new TypesDoNotMatch
        }
      case JObject(obj) =>
        if (allSameType(obj.iterator.map(_._2))) {
          "MAP_TYPE"
        } else {
          throw new TypesDoNotMatch
        }
    }
  }

  private def allSameType(values: Iterator[JValue]): Boolean = {
    if (values.hasNext) {
      val type_name = convertTableType(values.next())
      values.forall { case value => type_name.equals(convertTableType(value)) }
    } else {
      true
    }
  }

  private def executeTableMagic(name: String): Interpreter.ExecuteResponse = {
    val value = sparkIMain.valueOfTerm(name) match {
      case Some(obj: RDD[_]) => obj.asInstanceOf[RDD[_]].take(10)
      case Some(obj) => obj
      case None => return Interpreter.ExecuteError("NameError", f"Value $name does not exist")
    }

    extractTableFromJValue(Extraction.decompose(value))
  }

  private def extractTableFromJValue(value: JValue): Interpreter.ExecuteResponse = {
    // Convert the value into JSON and map it to a table.
    val rows: List[JValue] = value match {
      case JArray(arr) => arr
      case _ => List(value)
    }

    try {
      val headers = scala.collection.mutable.Map[String, Map[String, String]]()

      val data = rows.map { case row =>
        val cols: List[JField] = row match {
          case JArray(arr: List[JValue]) =>
            arr.zipWithIndex.map { case (v, index) => JField(index.toString, v) }
          case JObject(obj) => obj.sortBy(_._1)
          case value: JValue => List(JField("0", value))
        }

        cols.map { case (k, v) =>
          val typeName = convertTableType(v)

          headers.get(k) match {
            case Some(header) =>
              if (header.get("type").get != typeName) {
                throw new TypesDoNotMatch
              }
            case None =>
              headers.put(k, Map(
                "type" -> typeName,
                "name" -> k
              ))
          }

          v
        }
      }

      Interpreter.ExecuteSuccess(
        repl.APPLICATION_LIVY_TABLE_JSON -> (
          ("headers" -> headers.toSeq.sortBy(_._1).map(_._2)) ~ ("data" -> data)
        ))
    } catch {
      case _: TypesDoNotMatch =>
        Interpreter.ExecuteError("TypeError", "table rows have different types")
    }
  }

  private def executeLines(lines: List[String], result: Interpreter.ExecuteResponse): Interpreter.ExecuteResponse = {
    lines match {
      case Nil => result
      case head :: tail =>
        val result = executeLine(head)

        result match {
          case Interpreter.ExecuteIncomplete() =>
            tail match {
              case Nil =>
                result

              case next :: nextTail =>
                executeLines(head + "\n" + next :: nextTail, result)
            }
          case Interpreter.ExecuteError(_, _, _) =>
            result

          case _ =>
            executeLines(tail, result)
        }
    }
  }

  private def executeLine(code: String): Interpreter.ExecuteResponse = {
    code match {
      case MAGIC_REGEX(magic, rest) =>
        executeMagic(magic, rest)
      case _ =>
        scala.Console.withOut(outputStream) {
          sparkIMain.interpret(code) match {
            case Results.Success =>
              Interpreter.ExecuteSuccess(
                repl.TEXT_PLAIN -> readStdout()
              )
            case Results.Incomplete => Interpreter.ExecuteIncomplete()
            case Results.Error => Interpreter.ExecuteError("Error", readStdout())
          }
        }
    }
  }

  private def readStdout() = {
    val output = outputStream.toString("UTF-8").trim
    outputStream.reset()

    output
  }
}
