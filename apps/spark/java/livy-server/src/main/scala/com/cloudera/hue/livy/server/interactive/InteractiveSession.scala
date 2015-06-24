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

package com.cloudera.hue.livy.server.interactive

import java.net.URL
import java.util.concurrent.TimeoutException

import com.cloudera.hue.livy.Utils
import com.cloudera.hue.livy.msgs.ExecuteRequest
import com.cloudera.hue.livy.server.Session
import com.cloudera.hue.livy.sessions.{Kind, State}

import scala.concurrent._
import scala.concurrent.duration.Duration

object InteractiveSession {
  class SessionFailedToStart(msg: String) extends Exception(msg)

  class StatementNotFound extends Exception
}

trait InteractiveSession extends Session {
  def kind: Kind

  def proxyUser: Option[String]

  override def lastActivity: Option[Long]

  def url: Option[URL]

  def url_=(url: URL)

  def executeStatement(content: ExecuteRequest): Statement

  def statements: IndexedSeq[Statement]

  def interrupt(): Future[Unit]

  @throws(classOf[TimeoutException])
  @throws(classOf[InterruptedException])
  final def waitForStateChange(oldState: State, atMost: Duration) = {
    Utils.waitUntil({ () => state != oldState }, atMost)
  }
}

