package com.cloudera.hue.livy.repl.scala.interpreter

import java.io.{StringWriter, BufferedReader, StringReader}
import java.util.concurrent.SynchronousQueue

import org.apache.spark.repl.SparkILoop

import scala.annotation.tailrec
import scala.concurrent.{ExecutionContext, Future, Promise}
import scala.tools.nsc.SparkHelper
import scala.tools.nsc.interpreter.{Formatting, JPrintWriter}
import scala.tools.nsc.util.ClassPath

object Interpreter {
  sealed trait State
  case class Starting() extends State
  case class Idle() extends State
  case class Busy() extends State
  case class ShuttingDown() extends State
}

class Interpreter {
  private implicit def executor: ExecutionContext = ExecutionContext.global

  private val queue = new SynchronousQueue[Request]()

  // We start up the ILoop in it's own class loader because the SparkILoop store
  // itself in a global variable.
  private val iloop = {
    val classLoader = new ILoopClassLoader(classOf[Interpreter].getClassLoader)
    val cls = classLoader.loadClass(classOf[ILoop].getName)
    val constructor = cls.getConstructor(classOf[SynchronousQueue[Request]])
    constructor.newInstance(queue).asInstanceOf[ILoop]
  }

  // We also need to start the ILoop in it's own thread because it wants to run
  // inside a loop.
  private val thread = new Thread {
    override def run() = {
      val args = Array("-usejavacp")
      iloop.process(args)
    }
  }

  thread.start()

  def state = iloop.state

  def execute(code: String): Future[ExecuteResponse] = {
    val promise = Promise[ExecuteResponse]()
    queue.put(ExecuteRequest(code, promise))
    promise.future
  }

  def shutdown(): Future[Unit] = {
    val promise = Promise[Unit]()
    queue.put(ShutdownRequest(promise))
    promise.future.map({ case () => thread.join() })
  }
}

private class ILoopClassLoader(classLoader: ClassLoader) extends ClassLoader(classLoader) { }

private sealed trait Request
private case class ExecuteRequest(code: String, promise: Promise[ExecuteResponse]) extends Request
private case class ShutdownRequest(promise: Promise[Unit]) extends Request

case class ExecuteResponse(executionCount: Int, data: String)

private class ILoop(queue: SynchronousQueue[Request], outWriter: StringWriter) extends SparkILoop(
  new BufferedReader(new StringReader("")),
  new JPrintWriter(outWriter)
) {
  def this(queue: SynchronousQueue[Request]) = this(queue, new StringWriter)

  var _state: Interpreter.State = Interpreter.Starting()

  var _executionCount = 0

  def state = _state

  org.apache.spark.repl.Main.interp = this

  private class ILoopInterpreter extends SparkILoopInterpreter {
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
    def readOneLine() = queue.take()

    // return false if repl should exit
    def processLine(request: Request): Boolean = {
      _state = Interpreter.Busy()

      if (isAsync) {
        if (!awaitInitialized()) return false
        runThunks()
      }

      request match {
        case ExecuteRequest(statement, promise) =>
          _executionCount += 1

          command(statement) match {
            case Result(false, _) => false
            case Result(true, finalLine) =>
              finalLine match {
                case Some(line) => addReplay(line)
                case None =>
              }

              var output = outWriter.getBuffer.toString

              // Strip the trailing '\n'
              output = output.stripSuffix("\n")

              outWriter.getBuffer.setLength(0)

              promise.success(ExecuteResponse(_executionCount - 1, output))

              true
          }
        case ShutdownRequest(promise) =>
          promise.success(())
          false
      }
    }

    @tailrec
    def innerLoop() {
      _state = Interpreter.Idle()

      outWriter.getBuffer.setLength(0)

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
