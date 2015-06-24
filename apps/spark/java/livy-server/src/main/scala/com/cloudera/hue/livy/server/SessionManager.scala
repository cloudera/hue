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

import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.atomic.AtomicInteger

import com.cloudera.hue.livy.Logging

import scala.collection.JavaConversions._
import scala.concurrent.{ExecutionContext, Future}

abstract class SessionManager[S <: Session, C](factory: SessionFactory[S, C])
  extends Logging
{
  private implicit def executor: ExecutionContext = ExecutionContext.global

  protected[this] val _idCounter = new AtomicInteger()
  protected[this] val _sessions = new ConcurrentHashMap[Int, S]()

  def create(createRequest: C): Future[S] = {
    val id = _idCounter.getAndIncrement
    val session: Future[S] = factory.create(id, createRequest)

    session.map({ case(session) =>
      info("created session %s" format session.id)
      _sessions.put(session.id, session)
      session
    })
  }

  def get(id: Int): Option[S] = Option(_sessions.get(id))

  def all(): Seq[S] = _sessions.values().toSeq

  def delete(id: Int): Future[Unit] = {
    get(id) match {
      case Some(session) => delete(session)
      case None => Future.successful(())
    }
  }

  def delete(session: S): Future[Unit] = {
    session.stop().map { case _ =>
      _sessions.remove(session.id)
        Unit
    }
  }

  def remove(id: Int): Option[S] = {
    Option(_sessions.remove(id))
  }

  def shutdown(): Unit = {}
}
