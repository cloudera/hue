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
import com.cloudera.hue.livy.sessions.interactive.InteractiveSession
import com.cloudera.hue.livy.spark.SparkProcess

import scala.annotation.tailrec
import scala.concurrent.Future

object InteractiveSessionProcess extends Logging {

  def apply(id: Int,
            process: SparkProcess,
            createInteractiveRequest: CreateInteractiveRequest): InteractiveSession = {
    new InteractiveSessionProcess(id, process, createInteractiveRequest)
  }
}

private class InteractiveSessionProcess(id: Int,
                                        process: SparkProcess,
                                        request: CreateInteractiveRequest)
  extends InteractiveWebSession(id, process, request) {

  val stdoutThread = new Thread {
    override def run() = {
      val regex = """Starting livy-repl on (https?://.*)""".r

      val lines = process.inputIterator

      // Loop until we find the ip address to talk to livy-repl.
      @tailrec
      def readUntilURL(): Unit = {
        if (lines.hasNext) {
          val line = lines.next()

          line match {
            case regex(url_) => url = new URL(url_)
            case _ => readUntilURL()
          }
        }
      }

      readUntilURL()
    }
  }

  stdoutThread.setName("process session stdout reader")
  stdoutThread.setDaemon(true)
  stdoutThread.start()

  override def stop(): Future[Unit] = {
    super.stop().andThen { case r =>
      stdoutThread.join()
      r
    }
  }
}
