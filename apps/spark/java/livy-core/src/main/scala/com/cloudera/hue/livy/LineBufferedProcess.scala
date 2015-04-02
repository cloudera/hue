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

package com.cloudera.hue.livy

import scala.io.Source

class LineBufferedProcess(process: Process) extends Logging {

  private[this] var _stdoutLines: IndexedSeq[String] = IndexedSeq()
  private[this] var _stderrLines: IndexedSeq[String] = IndexedSeq()

  private val stdoutThread = new Thread {
    override def run() = {
      val lines = Source.fromInputStream(process.getInputStream).getLines()
      for (line <- lines) {
        trace("stdout: ", line)
        _stdoutLines +:= line
      }
    }
  }
  stdoutThread.setDaemon(true)
  stdoutThread.start()

  private val stderrThread = new Thread {
    override def run() = {
      val lines = Source.fromInputStream(process.getErrorStream).getLines()
      for (line <- lines) {
        trace("stderr: ", line)
        _stderrLines +:= line
      }
    }
  }
  stderrThread.setDaemon(true)
  stderrThread.start()

  def stdoutLines: IndexedSeq[String] = _stdoutLines

  def stderrLines: IndexedSeq[String] = _stderrLines

  def destroy(): Unit = {
    process.destroy()
  }

  def exitValue(): Int = {
    process.exitValue()
  }

  def waitFor(): Int = {
    val output = process.waitFor()
    stdoutThread.join()
    stderrThread.join()
    output
  }
}
