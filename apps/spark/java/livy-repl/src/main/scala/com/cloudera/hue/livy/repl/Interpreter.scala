package com.cloudera.hue.livy.repl

import java.io.{BufferedReader, PipedReader, PipedWriter, StringWriter}
import java.util.concurrent.{BlockingQueue, SynchronousQueue}

import com.cloudera.hue.livy.{Complete, ExecuteResponse}
import org.apache.spark.repl.SparkILoop

import scala.annotation.tailrec
import scala.concurrent._
import scala.tools.nsc.SparkHelper
import scala.tools.nsc.interpreter.{Formatting, _}
import scala.tools.nsc.util.ClassPath

class SparkInterpreter {
  private implicit def executor: ExecutionContext = ExecutionContext.global

  private val inQueue = new SynchronousQueue[Request]
  private val inWriter = new PipedWriter()

  org.apache.spark.repl.Main.interp = new ILoop(
    this,
    inQueue,
    new BufferedReader(new PipedReader(inWriter)),
    new StringWriter)

  // Launch the real interpreter thread.
  private val thread = new Thread {
    override def run(): Unit = {
      val args = Array("-usejavacp")
      org.apache.spark.repl.Main.interp.process(args)
    }
  }
  thread.start()

  def statements = {
    org.apache.spark.repl.Main.interp.history.asStrings
  }

  def execute(statement: String): Future[com.cloudera.hue.livy.ExecuteResponse] = {
    val promise = Promise[ExecuteResponse]()
    inQueue.put(ExecuteRequest(statement, promise))
    promise.future
  }

  def close(): Unit = {
    inQueue.put(ShutdownRequest())
    thread.join()
  }
}

private class ILoop(parent: SparkInterpreter, inQueue: BlockingQueue[Request], in0: BufferedReader, outString: StringWriter) extends SparkILoop(in0, new JPrintWriter(outString)) {

  class ILoopInterpreter extends SparkILoopInterpreter {
    outer =>

    override lazy val formatting = new Formatting {
      def prompt = ILoop.this.prompt
    }
    override protected def parentClassLoader = SparkHelper.explicitParentLoader(settings).getOrElse(classOf[SparkILoop].getClassLoader)
  }

  /** Create a new interpreter. */
  override def createInterpreter() {
    require(settings != null)

    if (addedClasspath != "") settings.classpath.append(addedClasspath)
    // work around for Scala bug
    val totalClassPath = SparkILoop.getAddedJars.foldLeft(
      settings.classpath.value)((l, r) => ClassPath.join(l, r))
    this.settings.classpath.value = totalClassPath

    intp = new ILoopInterpreter
  }

  private val replayQuestionMessage =
    """|That entry seems to have slain the compiler.  Shall I replay
      |your session? I can re-run each line except the last one.
      |[y/n]
    """.trim.stripMargin

  private def crashRecovery(ex: Throwable): Boolean = {
    echo(ex.toString)
    ex match {
      case _: NoSuchMethodError | _: NoClassDefFoundError =>
        echo("\nUnrecoverable error.")
        throw ex
      case _  =>
        def fn(): Boolean =
          try in.readYesOrNo(replayQuestionMessage, { echo("\nYou must enter y or n.") ; fn() })
          catch { case _: RuntimeException => false }

        if (fn()) replay()
        else echo("\nAbandoning crashed session.")
    }
    true
  }

  override def prompt = ""

  override def loop(): Unit = {
    def readOneLine() = {
      inQueue.take()
    }

    // return false if repl should exit
    def processLine(request: Request): Boolean = {
      if (isAsync) {
        if (!awaitInitialized()) return false
        runThunks()
      }

      request match {
        case ExecuteRequest(statement, promise) =>
          command(statement) match {
            case Result(false, _) => false
            case Result(true, finalLine) =>
              finalLine match {
                case Some(line) => addReplay(line)
                case _ =>
              }

              var output: String = outString.getBuffer.toString
              output = output.substring(0, output.length - 1)
              outString.getBuffer.setLength(0)

              val statement = ExecuteResponse(0, Complete(), List(), List(output))
              promise.success(statement)

              true
          }
        case ShutdownRequest() => false
      }
    }

    @tailrec
    def innerLoop() {
      outString.getBuffer.setLength(0)

      val shouldContinue = try {
        processLine(readOneLine())
      } catch {
        case t: Throwable => crashRecovery(t)
      }

      if (shouldContinue) {
        innerLoop()
      }
    }

    innerLoop()
  }
}

private sealed trait Request
private case class ExecuteRequest(statement: String, promise: Promise[ExecuteResponse]) extends Request
private case class ShutdownRequest() extends Request
