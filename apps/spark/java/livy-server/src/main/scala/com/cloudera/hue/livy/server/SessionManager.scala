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

package com.cloudera.hue.livy.server

import java.util.concurrent.atomic.AtomicInteger

import com.cloudera.hue.livy.{LivyConf, Logging}
import org.json4s.JValue

import scala.collection.mutable
import scala.concurrent.{ExecutionContext, Future}

class SessionManager[S <: Session](livyConf: LivyConf, factory: SessionFactory[S])
  extends Logging {

  private implicit def executor: ExecutionContext = ExecutionContext.global

  private[this] val _idCounter = new AtomicInteger()
  private[this] val _sessions = mutable.Map[Int, S]()

  private[this] val sessionTimeout = livyConf.getInt("livy.server.session.timeout", 1000 * 60 * 60)
  private[this] val garbageCollector = new GarbageCollector
  garbageCollector.setDaemon(true)
  garbageCollector.start()

  def create(createRequest: JValue): S = {
    val id = _idCounter.getAndIncrement
    val session: S = factory.create(id, createRequest)

    info("created session %s" format session.id)

    synchronized {
      _sessions.put(session.id, session)
      session
    }
  }

  def get(id: Int): Option[S] = _sessions.get(id)

  def size(): Int = _sessions.size

  def all(): Iterable[S] = _sessions.values

  def delete(id: Int): Option[Future[Unit]] = {
    get(id).map(delete)
  }

  def delete(session: S): Future[Unit] = {
    session.stop().map { case _ =>
      synchronized {
        _sessions.remove(session.id)
      }

      Unit
    }
  }

  def shutdown(): Unit = {}

  def collectGarbage() = {
    def expired(session: Session): Boolean = {
      session.lastActivity match {
        case Some(lastActivity) => System.currentTimeMillis() - lastActivity > sessionTimeout
        case None => false
      }
    }

    all().filter(expired).foreach(delete)
  }

  private class GarbageCollector extends Thread("session gc thread") {

    private var finished = false

    override def run(): Unit = {
      while (!finished) {
        collectGarbage()
        Thread.sleep(60 * 1000)
      }
    }

    def shutdown(): Unit = {
      finished = true
    }
  }
}
