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

package com.cloudera.hue.livy.msgs

sealed trait MsgType {
}
object MsgType {
  case object execute_request extends MsgType
  case object execute_reply extends MsgType
}

case class Msg[T <: Content](msg_type: MsgType, content: T)

sealed trait Content

case class ExecuteRequest(code: String) extends Content {
  val msg_type = MsgType.execute_request
}

sealed trait ExecutionStatus
object ExecutionStatus {
  case object ok extends ExecutionStatus
  case object error extends ExecutionStatus
  case object abort extends ExecutionStatus
}

sealed trait ExecuteReply extends Content {
  val msg_type = MsgType.execute_reply

  val status: ExecutionStatus
  val execution_count: Int
}

case class ExecuteReplyOk(execution_count: Int,
                          payload: Map[String, String]) extends ExecuteReply {
  val status = ExecutionStatus.ok
}

case class ExecuteReplyError(execution_count: Int,
                             ename: String,
                             evalue: String,
                             traceback: List[String]) extends ExecuteReply {
  val status = ExecutionStatus.error
}

case class ExecuteResponse(id: Int, input: Seq[String], output: Seq[String])

case class ShutdownRequest() extends Content
