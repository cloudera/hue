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

package com.cloudera.hue.livy.sessions

sealed trait State

case class NotStarted() extends State {
  override def toString = "not_started"
}

case class Starting() extends State {
  override def toString = "starting"
}

case class Idle() extends State {
  override def toString = "idle"
}

case class Running() extends State {
  override def toString = "running"
}

case class Busy() extends State {
  override def toString = "busy"
}

case class Error() extends State {
  override def toString = "error"
}

case class ShuttingDown() extends State {
  override def toString = "shutting_down"
}

case class Dead() extends State {
  override def toString = "dead"
}

case class Success() extends State {
  override def toString = "success"
}
