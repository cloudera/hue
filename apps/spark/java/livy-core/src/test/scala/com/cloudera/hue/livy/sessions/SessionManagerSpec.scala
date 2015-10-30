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

import com.cloudera.hue.livy.LivyConf
import org.json4s.JsonAST.{JNothing, JValue}
import org.scalatest.{FlatSpec, Matchers}

import scala.concurrent.duration.Duration
import scala.concurrent.{Await, Future}

class SessionManagerSpec extends FlatSpec with Matchers {

  class MockSession(val id: Int) extends Session {
    override def stop(): Future[Unit] = Future.successful(())

    override def logLines(): IndexedSeq[String] = IndexedSeq()

    override def state: SessionState = SessionState.Success(0)
  }

  class MockSessionFactory extends SessionFactory[MockSession] {
    override def create(id: Int, createRequest: JValue): MockSession = new MockSession(id)
  }

  it should "garbage collect old sessions" in {
    val livyConf = new LivyConf()
    livyConf.set(SessionManager.SESSION_TIMEOUT, "100")
    val manager = new SessionManager(livyConf, new MockSessionFactory)
    val session = manager.create(JNothing)
    manager.get(session.id).isDefined should be(true)
    Await.result(manager.collectGarbage(), Duration.Inf)
    manager.get(session.id).isEmpty should be(true)
  }
}
