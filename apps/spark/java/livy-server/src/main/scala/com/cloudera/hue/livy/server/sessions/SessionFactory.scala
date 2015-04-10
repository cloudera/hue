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

import com.cloudera.hue.livy.LivyConf
import com.cloudera.hue.livy.sessions.Kind
import com.cloudera.hue.livy.yarn.Client

import scala.concurrent.{ExecutionContext, Future}

trait SessionFactory {
  def createSession(id: Int, kind: Kind, proxyUser: Option[String] = None): Future[Session]

  def close(): Unit = {}
}

class ThreadSessionFactory(livyConf: LivyConf) extends SessionFactory {

  implicit def executor: ExecutionContext = ExecutionContext.global

  override def createSession(id: Int, kind: Kind, proxyUser: Option[String] = None): Future[Session] = {
    Future {
      ThreadSession.create(id, kind)
    }
  }
}

class ProcessSessionFactory(livyConf: LivyConf) extends SessionFactory {

  implicit def executor: ExecutionContext = ExecutionContext.global

  override def createSession(id: Int, kind: Kind, proxyUser: Option[String] = None): Future[Session] = {
    Future {
      ProcessSession.create(livyConf, id, kind, proxyUser)
    }
  }
}

class YarnSessionFactory(livyConf: LivyConf) extends SessionFactory {

  implicit def executor: ExecutionContext = ExecutionContext.global

  val client = new Client(livyConf)

  override def createSession(id: Int, kind: Kind, proxyUser: Option[String] = None): Future[Session] = {
    Future {
      YarnSession.create(livyConf, client, id, kind, proxyUser)
    }
  }

  override def close(): Unit = {
    client.close()
  }
}
