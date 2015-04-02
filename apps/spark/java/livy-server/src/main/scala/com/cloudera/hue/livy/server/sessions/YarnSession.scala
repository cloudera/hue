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

package com.cloudera.hue.livy.server.sessions

import java.util.concurrent.TimeUnit

import com.cloudera.hue.livy.sessions.{Kind, Error}
import com.cloudera.hue.livy.yarn.{Client, Job}

import scala.concurrent.{Await, ExecutionContext, ExecutionContextExecutor, Future}
import scala.concurrent.duration._

object YarnSession {
  protected implicit def executor: ExecutionContextExecutor = ExecutionContext.global

  def create(client: Client, id: String, kind: Kind, proxyUser: Option[String] = None): Future[Session] = {
    val callbackUrl = System.getProperty("livy.server.callback-url")
    val job = client.submitApplication(
      id = id,
      kind = kind.toString,
      proxyUser = proxyUser,
      callbackUrl = callbackUrl)

    Future.successful(new YarnSession(id, kind, proxyUser, job))
  }
}

private class YarnSession(id: String,
                          kind: Kind,
                          proxyUser: Option[String],
                          job: Future[Job]) extends WebSession(id, kind, proxyUser) {
  job.onFailure { case _ =>
    _state = Error()
  }

  override def stop(): Future[Unit] = {
    super.stop().andThen {
      case _ =>
        try {
          val job_ = Await.result(job, Duration(1, TimeUnit.SECONDS))
          job_.waitForFinish(10000)
        } catch {
          case e: Throwable =>
            _state = Error()
            throw e
        }
    }
  }
}
