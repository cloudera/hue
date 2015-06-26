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

import com.cloudera.hue.livy.Logging
import org.json4s.JValue

import scala.collection.mutable
import scala.concurrent.{ExecutionContext, Future}

object SessionManager {
  // Time in milliseconds; TODO: make configurable
  val TIMEOUT = 60000

  // Time in milliseconds; TODO: make configurable
  val GC_PERIOD = 1000 * 60 * 60
}

class SessionManager[S <: Session](factory: SessionFactory[S])
  extends Logging {

  import SessionManager._

  private implicit def executor: ExecutionContext = ExecutionContext.global

  protected[this] val _idCounter = new AtomicInteger()
  protected[this] val _sessions = mutable.Map[Int, S]()

  private val garbageCollector = new GarbageCollector
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
        case Some(lastActivity) => System.currentTimeMillis() - lastActivity > TIMEOUT
        case None => false
      }
    }

    all().filter(expired).foreach(delete)
  }

  private class GarbageCollector extends Thread {

    private var finished = false

    override def run(): Unit = {
      while (!finished) {
        collectGarbage()
        Thread.sleep(SessionManager.GC_PERIOD)
      }
    }

    def shutdown(): Unit = {
      finished = true
    }
  }
}
