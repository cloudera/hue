package com.cloudera.hue.livy.repl

import java.io._
import java.util.concurrent.{BlockingQueue, SynchronousQueue}

import com.cloudera.hue.livy.{Complete, ExecuteResponse}
import org.apache.spark.repl.SparkILoop

import scala.annotation.tailrec
import scala.concurrent._
import scala.concurrent.duration.Duration
import scala.tools.nsc.SparkHelper
import scala.tools.nsc.interpreter.{Formatting, _}
import scala.tools.nsc.util.ClassPath

class SparkInterpreter {
  private implicit def executor: ExecutionContext = ExecutionContext.global

  private val inQueue = new SynchronousQueue[ILoop.Request]

  org.apache.spark.repl.Main.interp = new ILoop(inQueue)

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

  def execute(statement: String): Future[ExecuteResponse] = {
    val promise = Promise[ILoop.ExecuteResponse]()
    inQueue.put(ILoop.ExecuteRequest(statement, promise))

    for {
      rep <- promise.future
    } yield ExecuteResponse(0, List(statement), List(rep.output))
  }

  def close(): Unit = {
    val promise = Promise[ILoop.ShutdownResponse]()
    inQueue.put(ILoop.ShutdownRequest(promise))

    Await.result(promise.future, Duration.Inf)

    thread.join()
  }
}

private object ILoop {
  sealed trait Request
  case class ExecuteRequest(statement: String, promise: Promise[ExecuteResponse]) extends Request
  case class ShutdownRequest(promise: Promise[ShutdownResponse]) extends Request

  case class ExecuteResponse(output: String)
  case class ShutdownResponse()
}

// FIXME: The spark interpreter is written to own the event loop, so we need to invert it so we can inject our commands into it.
private class ILoop(inQueue: BlockingQueue[ILoop.Request], outString: StringWriter = new StringWriter)
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
              output = output.substring(0, output.length - 1)

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
