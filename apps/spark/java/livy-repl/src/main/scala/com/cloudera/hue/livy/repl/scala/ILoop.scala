package com.cloudera.hue.livy.repl.scala

import java.io._
import java.util.concurrent.BlockingQueue

import org.apache.spark.repl.SparkILoop

import scala.annotation.tailrec
import scala.concurrent._
import scala.tools.nsc.SparkHelper
import scala.tools.nsc.interpreter.{Formatting, _}
import scala.tools.nsc.util.ClassPath

object ILoop {
  sealed trait Request
  case class ExecuteRequest(statement: String, promise: Promise[ExecuteResponse]) extends Request
  case class ShutdownRequest(promise: Promise[ShutdownResponse]) extends Request

  case class ExecuteResponse(output: String)
  case class ShutdownResponse()
}

// FIXME: The spark interpreter is written to own the event loop, so we need to invert it so we can inject our commands into it.
class ILoop(inQueue: BlockingQueue[ILoop.Request], outString: StringWriter = new StringWriter)
  extends SparkILoop(
    // we don't actually use the reader, so pass in a null reader for now.
    new BufferedReader(new StringReader("")),
    new JPrintWriter(outString)) {

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
    def processLine(request: ILoop.Request): Boolean = {
      if (isAsync) {
        if (!awaitInitialized()) return false
        runThunks()
      }

      request match {
        case ILoop.ExecuteRequest(statement, promise) =>
          command(statement) match {
            case Result(false, _) => false
            case Result(true, finalLine) =>
              finalLine match {
                case Some(line) => addReplay(line)
                case None =>
              }

              var output = outString.getBuffer.toString

              // Strip the trailing '\n'
              output = output.stripSuffix("\n")

              outString.getBuffer.setLength(0)

              promise.success(ILoop.ExecuteResponse(output))

              true
          }
        case ILoop.ShutdownRequest(promise) =>
          promise.success(ILoop.ShutdownResponse())
          false
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
