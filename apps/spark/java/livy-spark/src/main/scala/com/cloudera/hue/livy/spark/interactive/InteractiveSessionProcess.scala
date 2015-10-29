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

package com.cloudera.hue.livy.spark.interactive

import java.net.URL

import com.cloudera.hue.livy.Logging
import com.cloudera.hue.livy.sessions.SessionState
import com.cloudera.hue.livy.sessions.interactive.InteractiveSession
import com.cloudera.hue.livy.spark.SparkProcess

import scala.annotation.tailrec
import scala.concurrent.Future

object InteractiveSessionProcess extends Logging {

  val CONF_LIVY_REPL_JAR = "livy.repl.jar"
  val CONF_LIVY_REPL_CALLBACK_URL = "livy.repl.callback-url"
  val CONF_LIVY_REPL_DRIVER_CLASS_PATH = "livy.repl.driverClassPath"

  def apply(id: Int,
            process: SparkProcess,
            createInteractiveRequest: CreateInteractiveRequest): InteractiveSession = {
    new InteractiveSessionProcess(id, process, createInteractiveRequest)
  }
}

private class InteractiveSessionProcess(id: Int,
                                        process: SparkProcess,
                                        createInteractiveRequest: CreateInteractiveRequest)
  extends InteractiveWebSession(id, createInteractiveRequest) {

  val stdoutThread = new Thread {
    override def run() = {
      val regex = """Starting livy-repl on (https?://.*)""".r

      val lines = process.inputIterator

      // Loop until we find the ip address to talk to livy-repl.
      @tailrec
      def readUntilURL(): Boolean = {
        if (lines.hasNext) {
          val line = lines.next()
          println(line)

          line match {
            case regex(url_) =>
              url = new URL(url_)
              true
            case _ => readUntilURL()
          }
        } else {
          false
        }
      }

      if (readUntilURL()) {
        for (line <- lines) {
          println(line)
        }
      }
    }
  }

  stdoutThread.setName("process session stdout reader")
  stdoutThread.setDaemon(true)
  stdoutThread.start()

  // Error out the job if the process errors out.
  Future {
    if (process.waitFor() != 0) {
      _state = SessionState.Error()
    } else {
      // Set the state to done if the session shut down before contacting us.
      _state match {
        case (SessionState.Dead(_) | SessionState.Error(_) | SessionState.Success(_)) =>
        case _ =>
          _state = SessionState.Success()
      }
    }
  }

  override def logLines() = process.inputLines

  override def stop(): Future[Unit] = {
    super.stop().andThen { case r =>
      // Make sure the process is reaped.
      process.waitFor()
      stdoutThread.join()
      r
    }
  }
}
