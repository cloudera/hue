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

import java.io.InputStream
import java.util.concurrent.locks.ReentrantLock

import scala.io.Source

class LineBufferedStream(inputStream: InputStream) extends Logging {

  private[this] var _lines: IndexedSeq[String] = IndexedSeq()

  private[this] val _lock = new ReentrantLock()
  private[this] val _condition = _lock.newCondition()
  private[this] var _finished = false

  private val thread = new Thread {
    override def run() = {
      val lines = Source.fromInputStream(inputStream).getLines()
      for (line <- lines) {
        _lock.lock()
        try {
          trace("stdout: ", line)
          _lines = _lines :+ line
          _condition.signalAll()
        } finally {
          _lock.unlock()
        }
      }

      _lock.lock()
      try {
        _finished = true
        _condition.signalAll()
      } finally {
        _lock.unlock()
      }
    }
  }
  thread.setDaemon(true)
  thread.start()

  def lines: IndexedSeq[String] = _lines

  def iterator: Iterator[String] = {
    new LinesIterator
  }

  private class LinesIterator extends Iterator[String] {
    private[this] var index = 0

    override def hasNext: Boolean = {
      if (index < _lines.length) {
        true
      } else {
        // Otherwise we might still have more data.
        _lock.lock()
        try {
          if (_finished) {
            false
          } else {
            _condition.await()
            index < _lines.length
          }
        } finally {
          _lock.unlock()
        }
      }
    }

    override def next(): String = {
      val line = _lines(index)
      index += 1
      line
    }
  }
}
