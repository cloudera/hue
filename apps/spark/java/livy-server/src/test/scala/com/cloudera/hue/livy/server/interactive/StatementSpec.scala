/*
 * Licensed to Cloudera, Inc. under one
      val statement = Statement(
        0,
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

package com.cloudera.hue.livy.server.interactive

import com.cloudera.hue.livy.msgs.ExecuteRequest
import org.json4s.JsonAST.JString
import org.json4s.{DefaultFormats, Extraction}
import org.scalatest.{FunSpec, Matchers}

import scala.concurrent.duration.Duration
import scala.concurrent.{Await, Future}

class StatementSpec extends FunSpec with Matchers {

  implicit val formats = DefaultFormats

  describe("A statement") {
    it("should support paging through text/plain data") {
      val lines = List("1", "2", "3", "4", "5")
      val rep = Extraction.decompose(Map(
        "status" -> "ok",
        "execution_count" -> 0,
        "data" -> Map(
          "text/plain" -> lines.mkString("\n")
        )
      ))
      val stmt = new Statement(0, ExecuteRequest(""), Future.successful(rep))
      var output = Await.result(stmt.output(), Duration.Inf)
      output \ "data" \ "text/plain" should equal (JString(lines.mkString("\n")))

      output = Await.result(stmt.output(Some(2)), Duration.Inf)
      output \ "data" \ "text/plain" should equal (JString(lines.slice(2, lines.length).mkString("\n")))

      output = Await.result(stmt.output(Some(2), Some(1)), Duration.Inf)
      output \ "data" \ "text/plain" should equal (JString(lines.slice(2, 3).mkString("\n")))
    }

    it("should support paging through application/json arrays") {
      val lines = List("1", "2", "3", "4")
      val rep = Extraction.decompose(Map(
        "status" -> "ok",
        "execution_count" -> 0,
        "data" -> Map(
          "application/json" -> List(1, 2, 3, 4)
        )
      ))
      val stmt = new Statement(0, ExecuteRequest(""), Future.successful(rep))
      var output = Await.result(stmt.output(), Duration.Inf)
      (output \ "data" \ "application/json").extract[List[Int]] should equal (List(1, 2, 3, 4))

      output = Await.result(stmt.output(Some(2)), Duration.Inf)
      (output \ "data" \ "application/json").extract[List[Int]] should equal (List(3, 4))

      output = Await.result(stmt.output(Some(2), Some(1)), Duration.Inf)
      (output \ "data" \ "application/json").extract[List[Int]] should equal (List(3))
    }
  }

}
