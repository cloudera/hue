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

import java.net.URL

import com.cloudera.hue.livy.msgs.ExecuteRequest
import com.cloudera.hue.livy.repl.python.PythonSession
import com.cloudera.hue.livy.repl.scala.SparkSession
import com.cloudera.hue.livy.sessions.{Kind, PySpark, Spark, State}

import scala.collection.mutable.ArrayBuffer
import scala.concurrent.{ExecutionContext, ExecutionContextExecutor, Future}

object ThreadSession {
  val LIVY_HOME = System.getenv("LIVY_HOME")
  val LIVY_REPL = LIVY_HOME + "/bin/livy-repl"

  def create(id: String, kind: Kind): Session = {
    val session = kind match {
      case Spark() =>
        SparkSession.create()
      case PySpark() =>
        PythonSession.createPySpark()
    }
    new ThreadSession(id, kind, session)
  }
}

private class ThreadSession(val id: String,
                            val kind: Kind,
                            session: com.cloudera.hue.livy.repl.Session) extends Session {

  protected implicit def executor: ExecutionContextExecutor = ExecutionContext.global

  private var executedStatements = 0
  private var statements_ = new ArrayBuffer[Statement]

  override def proxyUser: Option[String] = None

  override def lastActivity: Long = 0

  override def state: State = session.state

  override def url: Option[URL] = None

  override def url_=(url: URL): Unit = {}

  override def executeStatement(content: ExecuteRequest): Statement = {
    val statement = new Statement(executedStatements, content, session.execute(content.code))

    executedStatements += 1
    statements_ += statement

    statement
  }

  override def statement(statementId: Int): Option[Statement] = statements_.lift(statementId)

  override def statements(): Seq[Statement] = statements_

  override def statements(fromIndex: Integer, toIndex: Integer): Seq[Statement] = statements_.slice(fromIndex, toIndex).toSeq

  override def interrupt(): Future[Unit] = {
    stop()
  }

  override def stop(): Future[Unit] = Future {
    session.close()
  }
}
