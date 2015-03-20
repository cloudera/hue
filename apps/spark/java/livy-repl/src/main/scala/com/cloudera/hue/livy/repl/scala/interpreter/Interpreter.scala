package com.cloudera.hue.livy.repl.scala.interpreter

import java.io._

import org.apache.spark.{SparkConf, SparkContext}
import org.apache.spark.repl.SparkIMain

import scala.concurrent.ExecutionContext
import scala.tools.nsc.Settings
import scala.tools.nsc.interpreter.{JPrintWriter, Results}


object Interpreter {
  sealed trait State
  case class NotStarted() extends State
  case class Starting() extends State
  case class Idle() extends State
  case class Busy() extends State
  case class ShuttingDown() extends State
  case class ShutDown() extends State
}

sealed abstract class ExecuteResponse(executeCount: Int)
case class ExecuteComplete(executeCount: Int, output: String) extends ExecuteResponse(executeCount)
case class ExecuteIncomplete(executeCount: Int, output: String) extends ExecuteResponse(executeCount)
case class ExecuteError(executeCount: Int, output: String) extends ExecuteResponse(executeCount)

class Interpreter {
  private implicit def executor: ExecutionContext = ExecutionContext.global

  private var _state: Interpreter.State = Interpreter.NotStarted()
  private val outputStream = new ByteArrayOutputStream()
  private var sparkIMain: SparkIMain = _
  private var sparkContext: SparkContext = _
  private var executeCount = 0

  def state = _state

  def start() = {
    require(_state == Interpreter.NotStarted() && sparkIMain == null)

    _state = Interpreter.Starting()

    class InterpreterClassLoader(classLoader: ClassLoader) extends ClassLoader(classLoader) {}
    val classLoader = new InterpreterClassLoader(classOf[Interpreter].getClassLoader)

    val settings = new Settings()
    settings.usejavacp.value = true

    sparkIMain = createSparkIMain(classLoader, settings)
    sparkIMain.initializeSynchronous()

    val sparkConf = new SparkConf(true)
      .setAppName("Livy Spark shell")
      .set("spark.repl.class.uri", sparkIMain.classServerUri)

    sparkContext = new SparkContext(sparkConf)

    sparkIMain.beQuietDuring {
      sparkIMain.bind("sc", "org.apache.spark.SparkContext", sparkContext, List("""@transient"""))
    }

    _state = Interpreter.Idle()
  }

  private def getMaster(): String = {
    sys.props.get("spark.master").getOrElse("local[*]")
  }

  private def createSparkIMain(classLoader: ClassLoader, settings: Settings) = {
    val out = new JPrintWriter(outputStream, true)
    val cls = classLoader.loadClass(classOf[SparkIMain].getName)
    val constructor = cls.getConstructor(classOf[Settings], classOf[JPrintWriter], java.lang.Boolean.TYPE)
    constructor.newInstance(settings, out, false: java.lang.Boolean).asInstanceOf[SparkIMain]
  }

  def execute(code: String): ExecuteResponse = {
    synchronized {
      executeCount += 1

      _state = Interpreter.Busy()

      val result = scala.Console.withOut(outputStream) {
        sparkIMain.interpret(code) match {
          case Results.Success =>
            val output = outputStream.toString("UTF-8").trim
            outputStream.reset()

            ExecuteComplete(executeCount - 1, output)

          case Results.Incomplete =>
            val output = outputStream.toString("UTF-8").trim
            outputStream.reset()

            ExecuteIncomplete(executeCount - 1, output)

          case Results.Error =>
            val output = outputStream.toString("UTF-8").trim
            outputStream.reset()
            ExecuteError(executeCount - 1, output)
        }
      }

      _state = Interpreter.Idle()

      result
    }
  }

  def shutdown(): Unit = {
    _state = Interpreter.ShuttingDown()

    if (sparkContext != null) {
      sparkContext.stop()
    }

    if (sparkIMain != null) {
      sparkIMain.close()
      sparkIMain = null
    }

    _state = Interpreter.ShutDown()
  }
}
