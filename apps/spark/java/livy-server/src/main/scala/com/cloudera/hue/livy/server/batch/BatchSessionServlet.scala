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

package com.cloudera.hue.livy.server.batch

import com.cloudera.hue.livy.Logging
import com.cloudera.hue.livy.server.{SessionManager, SessionServlet}
import org.json4s._

import scala.concurrent.{ExecutionContext, ExecutionContextExecutor}

object BatchSessionServlet extends Logging

class BatchSessionServlet(batchManager: SessionManager[BatchSession])
  extends SessionServlet[BatchSession](batchManager)
{
  override protected implicit def executor: ExecutionContextExecutor = ExecutionContext.global
  override protected implicit def jsonFormats: Formats = DefaultFormats ++ Serializers.Formats

  override protected def serializeSession(session: BatchSession) = Serializers.serializeBatch(session)

}

private object Serializers {
  import org.json4s.JsonDSL._

  def Formats: List[CustomSerializer[_]] = List(BatchSerializer)

  def serializeBatch(batch: BatchSession): JValue = {
    ("id", batch.id) ~
      ("state", batch.state.toString) ~
      ("log", getLogs(batch, None, Some(10))._3)
  }

  def getLogs(batch: BatchSession, fromOpt: Option[Int], sizeOpt: Option[Int]) = {
    val lines = batch.logLines()

    val size = sizeOpt.getOrElse(100)
    var from = fromOpt.getOrElse(-1)
    if (from < 0) {
      from = math.max(0, lines.length - size)
    }
    val until = from + size

    (from, lines.length, lines.view(from, until))
  }

  case object BatchSerializer extends CustomSerializer[BatchSession](
    implicit formats => ( {
    // We don't support deserialization.
    PartialFunction.empty
  }, {
    case batch: BatchSession => serializeBatch(batch)
  }
    )
  )
}
