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

class LineBufferedProcess(process: Process) extends Logging {

  private[this] val _inputStream = new LineBufferedStream(process.getInputStream)
  private[this] val _errorStream = new LineBufferedStream(process.getErrorStream)

  def inputLines: IndexedSeq[String] = _inputStream.lines
  def errorLines: IndexedSeq[String] = _errorStream.lines

  def inputIterator: Iterator[String] = _inputStream.iterator
  def errorIterator: Iterator[String] = _errorStream.iterator

  def destroy(): Unit = {
    process.destroy()
  }

  /** Returns if the process is still actively running. */
  def isAlive: Boolean = Utils.isProcessAlive(process)

  def exitValue(): Int = {
    process.exitValue()
  }

  def waitFor(): Int = {
    process.waitFor()
  }
}

