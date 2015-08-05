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

package com.cloudera.hue.livy.repl.process

import java.io.{BufferedReader, IOException, InputStreamReader, PrintWriter}
import java.util.concurrent.{LinkedBlockingQueue, TimeUnit}

import com.cloudera.hue.livy.Logging
import com.cloudera.hue.livy.repl.Interpreter
import com.cloudera.hue.livy.sessions._
import org.json4s.JValue

import scala.annotation.tailrec
import scala.concurrent.duration.Duration
import scala.concurrent.{Await, ExecutionContext, Future, Promise}
import scala.util

private sealed trait Request
private case class ExecuteRequest(code: String, promise: Promise[JValue]) extends Request
private case class ShutdownRequest(promise: Promise[Unit]) extends Request

abstract class ProcessInterpreter(process: Process)
  extends Interpreter
  with Logging
{
  implicit val executor: ExecutionContext = ExecutionContext.global

  protected[this] var _state: State = Starting()

  protected[this] val stdin = new PrintWriter(process.getOutputStream)
  protected[this] val stdout = new BufferedReader(new InputStreamReader(process.getInputStream), 1)

  private[this] val _queue = new LinkedBlockingQueue[Request]

  override def state: State = _state

  override def execute(code: String): Future[JValue] = {
    _state match {
      case (Dead() | ShuttingDown() | Error()) =>
        Future.failed(new IllegalStateException("interpreter is not running"))
      case _ =>
        val promise = Promise[JValue]()
        _queue.add(ExecuteRequest(code, promise))
        promise.future
    }
  }

  protected def waitUntilReady(): Unit

  protected def sendExecuteRequest(request: String): Option[JValue]

  protected def sendShutdownRequest(): Unit = {}

  private[this] val thread = new Thread("process interpreter") {
    override def run() = {
      waitUntilReady()

      _state = Idle()

      loop()
    }

    @tailrec
    private def loop(): Unit = {
      (_state, _queue.take()) match {
        case (Error(), ExecuteRequest(code, promise)) =>
          promise.failure(new Exception("session has been terminated"))
          loop()

        case (state, ExecuteRequest(code, promise)) =>
          require(state == Idle())

          _state = Busy()

          sendExecuteRequest(code) match {
            case Some(rep) =>
              synchronized {
                _state = Idle()
              }

              promise.success(rep)
            case None =>
              synchronized {
                _state = Error()
              }

              promise.failure(new Exception("session has been terminated"))
          }
          loop()

        case (_, ShutdownRequest(promise)) =>
          require(state == Idle() || state == Error())

          synchronized {
            _state = ShuttingDown()
          }

          try {
            sendShutdownRequest()

            try {
              process.getInputStream.close()
              process.getOutputStream.close()
            } catch {
              case _: IOException =>
            }

            try {
              process.destroy()
            } finally {
              synchronized {
                _state = Dead()
              }

              promise.success(())
            }
          }
      }
    }
  }

  thread.start()

  override def close(): Unit = {
    val future = synchronized {
      _state match {
        case (Dead() | ShuttingDown()) =>
          Future.successful()
        case _ =>
          val promise = Promise[Unit]()
          _queue.add(ShutdownRequest(promise))

          promise.future.andThen {
            case util.Success(_) =>
              thread.join()
            case util.Failure(_) =>
              thread.interrupt()
              thread.join()
          }
      }
    }

    // Give ourselves 10 seconds to tear down the process.
    try {
      Await.result(future, Duration(10, TimeUnit.SECONDS))
    } catch {
      case e: Throwable =>
        // Make sure if there are any problems we make sure we kill the process.
        process.destroy()
        thread.interrupt()
        throw e
    }
  }
}
