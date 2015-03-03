package com.cloudera.hue.livy.repl.python

import java.io._
import java.lang.ProcessBuilder.Redirect
import java.nio.file.Files
import java.util.concurrent.SynchronousQueue

import com.cloudera.hue.livy.Utils
import com.cloudera.hue.livy.repl.Session
import org.apache.spark.SparkContext
import org.json4s.jackson.JsonMethods._
import org.json4s.jackson.Serialization.write
import org.json4s.{DefaultFormats, JValue}
import py4j.GatewayServer

import scala.annotation.tailrec
import scala.collection.JavaConversions._
import scala.collection.mutable.ArrayBuffer
import scala.concurrent.{ExecutionContext, Future, Promise}

object PythonSession {
  def createPython(): Session = {
    create("python")
  }

  def createPySpark(): Session = {
    create(createFakePySpark().toString)
  }

  private def pythonPath = {
    val pythonPath = new ArrayBuffer[String]
    pythonPath ++= Utils.jarOfClass(classOf[SparkContext])
    pythonPath
  }

  private def create(driver: String) = {
    val pythonExec = sys.env.getOrElse("PYSPARK_DRIVER_PYTHON", "python")

    val gatewayServer = new GatewayServer(null, 0)
    gatewayServer.start()

    val builder = new ProcessBuilder(Seq(
      pythonExec,
      createFakeShell().toString
    ))

    val env = builder.environment()
    env.put("PYTHONPATH", pythonPath.mkString(File.pathSeparator))
    env.put("PYTHONUNBUFFERED", "YES")
    env.put("PYSPARK_GATEWAY_PORT", "" + gatewayServer.getListeningPort)
    env.put("SPARK_HOME", sys.env.getOrElse("SPARK_HOME", "."))

    builder.redirectError(Redirect.INHERIT)

    val process = builder.start()

    new PythonSession(process, gatewayServer)
  }

  private def createFakeShell(): File = {
    val source: InputStream = getClass.getClassLoader.getResourceAsStream("fake_shell.py")

    val file = Files.createTempFile("", "").toFile
    file.deleteOnExit()

    val sink = new FileOutputStream(file)
    val buf = new Array[Byte](1024)
    var n = source.read(buf)

    while (n > 0) {
      sink.write(buf, 0, n)
      n = source.read(buf)
    }

    source.close()
    sink.close()

    file
  }

  private def createFakePySpark(): File = {
    val source: InputStream = getClass.getClassLoader.getResourceAsStream("fake_pyspark.sh")

    val file = Files.createTempFile("", "").toFile
    file.deleteOnExit()

    file.setExecutable(true)

    val sink = new FileOutputStream(file)
    val buf = new Array[Byte](1024)
    var n = source.read(buf)

    while (n > 0) {
      sink.write(buf, 0, n)
      n = source.read(buf)
    }

    source.close()
    sink.close()

    file
  }
}

private class PythonSession(process: Process, gatewayServer: GatewayServer) extends Session {
  private implicit def executor: ExecutionContext = ExecutionContext.global

  implicit val formats = DefaultFormats

  private val stdin = new PrintWriter(process.getOutputStream)
  private val stdout = new BufferedReader(new InputStreamReader(process.getInputStream), 1)

  private var _history = ArrayBuffer[JValue]()
  private var _state: Session.State = Session.Starting()

  private val queue = new SynchronousQueue[Request]

  private val thread = new Thread {
    override def run() = {
      waitUntilReady()

      _state = Session.Idle()

      loop()
    }

    @tailrec
    def waitUntilReady(): Unit = {
      val line = stdout.readLine()
      line match {
        case null | "READY" =>
        case _ => waitUntilReady()
      }
    }

    @tailrec
    def loop(): Unit = {
      (_state, queue.take()) match {
        case (Session.Error(), ExecuteRequest(code, promise)) =>
          promise.failure(new Exception("session has been terminated"))
          loop()

        case (state, ExecuteRequest(code, promise)) =>
          require(state == Session.Idle())

          _state = Session.Busy()

          val msg = Map(
            "msg_type" -> "execute_request",
            "content" -> Map("code" -> code))

          stdin.println(write(msg))
          stdin.flush()

          val line = stdout.readLine()
          // The python process shut down
          if (line == null) {
            _state = Session.Error()
            promise.failure(new Exception("session has been terminated"))
          } else {
            val rep = parse(line)
            assert((rep \ "msg_type").extract[String] == "execute_reply")

            val content: JValue = rep \ "content"
            _history += content

            _state = Session.Idle()

            promise.success(content)
          }

          loop()

        case (_, ShutdownRequest(promise)) =>
          require(state == Session.Idle() || state == Session.Error())

          _state = Session.ShuttingDown()
          process.getInputStream.close()
          process.getOutputStream.close()
          process.destroy()
          _state = Session.ShutDown()
          promise.success(())
      }
    }
  }

  thread.start()

  override def state = _state

  override def history(): Seq[JValue] = _history

  override def history(id: Int): Option[JValue] = {
    if (id < _history.length) {
      Some(_history(id))
    } else {
      None
    }
  }

  override def execute(code: String): Future[JValue] = {
    val promise = Promise[JValue]()
    queue.put(ExecuteRequest(code, promise))
    promise.future
  }

  override def close(): Future[Unit] = synchronized {
    _state match {
      case Session.ShutDown() =>
        Future.successful(())
      case Session.ShuttingDown() =>
        Future {
          waitForStateChange(Session.ShuttingDown())
          Future.successful(())
        }
      case _ =>
        val promise = Promise[Unit]()
        queue.put(ShutdownRequest(promise))
        promise.future.map({ case () =>
          thread.join()
          gatewayServer.shutdown()
        })
    }
  }
}

private sealed trait Request
private case class ExecuteRequest(code: String, promise: Promise[JValue]) extends Request
private case class ShutdownRequest(promise: Promise[Unit]) extends Request

case class ExecuteResponse(content: JValue)
