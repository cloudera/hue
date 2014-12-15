package com.cloudera.hue.sparker.repl.interpreter

import java.io.{BufferedReader, PipedReader, PipedWriter, StringWriter}
import java.util.concurrent.{BlockingQueue, SynchronousQueue}

import org.apache.spark.repl.SparkILoop
import org.json4s.jackson.JsonMethods._

import scala.concurrent._
import scala.tools.nsc.SparkHelper
import scala.tools.nsc.interpreter.{Formatting, _}
import scala.tools.nsc.util.ClassPath

class SparkerInterpreter {
  private implicit def executor: ExecutionContext = ExecutionContext.global

  private val inQueue = new SynchronousQueue[Request]

  private val inWriter = new PipedWriter()

  // Launch the real interpreter thread.
  private val thread = new Thread {
    override def run(): Unit = {
      org.apache.spark.repl.Main.interp = new SparkerILoop(
        inQueue,
        new BufferedReader(new PipedReader(inWriter)),
        new StringWriter)
      val args = Array("-usejavacp")
      org.apache.spark.repl.Main.interp.process(args)
    }
  }
  thread.start()

  def execute(statement: String): Future[Map[String, String]] = {
    val promise = Promise[Map[String, String]]()
    inQueue.put(ExecuteRequest(statement, promise))
    promise.future
  }

  def close(): Unit = {
    inQueue.put(ShutdownRequest())
    thread.join()
  }
}

class SparkerILoop(inQueue: BlockingQueue[Request], in0: BufferedReader, outString: StringWriter) extends SparkILoop(in0, new JPrintWriter(outString)) {

  class SparkerILoopInterpreter extends SparkILoopInterpreter {
    outer =>

    override lazy val formatting = new Formatting {
      def prompt = SparkerILoop.this.prompt
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

    intp = new SparkerILoopInterpreter
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
        case ExecuteRequest(statement, promise) => {
          command(statement) match {
            case Result(false, _) => false
            case Result(true, finalLine) => {
              finalLine match {
                case Some(line) => addReplay(line)
                case _ =>
              }

              var output: String = outString.getBuffer.toString
              output = output.substring(0, output.length - 1)
              outString.getBuffer.setLength(0)

              promise.success(Map("type" -> "stdout", "stdout" -> output))

              true
            }
          }
        }
        case ShutdownRequest() => false
      }
    }
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

sealed trait Request
case class ExecuteRequest(statement: String, promise: Promise[Map[String, String]]) extends Request
case class ShutdownRequest() extends Request
