package com.cloudera.hue.livy.repl.python

import java.io._
import java.lang.ProcessBuilder.Redirect
import java.nio.file.Files

import com.cloudera.hue.livy.msgs.ExecuteRequest
import com.cloudera.hue.livy.repl.Session
import org.json4s.jackson.JsonMethods._
import org.json4s.jackson.Serialization.write
import org.json4s.{DefaultFormats, JValue}

import scala.collection.mutable.ArrayBuffer
import scala.concurrent.{ExecutionContext, Future}

object PythonSession {
  def createPython(): Session = {
    create("python")
  }

  def createPySpark(): Session = {
    create(createFakePySpark().toString)
  }

  private def create(driver: String) = {
    val fakeShell = createFakeShell()
    val pb = new ProcessBuilder(driver, fakeShell.toString)
    pb.redirectError(Redirect.INHERIT)
    val process = pb.start()
    val in = process.getInputStream
    val out = process.getOutputStream

    new PythonSession(process, in, out)
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

private class PythonSession(process: Process, in: InputStream, out: OutputStream) extends Session {
  private implicit def executor: ExecutionContext = ExecutionContext.global

  implicit val formats = DefaultFormats

  private[this] val stdin = new PrintWriter(out)
  private[this] val stdout = new BufferedReader(new InputStreamReader(in), 1)

  private[this] var _statements = ArrayBuffer[JValue]()

  override def statements: Seq[JValue] = _statements

  override def execute(content: ExecuteRequest): Future[JValue] = {
    Future {
      val msg = Map("msg_type" -> "execute_request", "content" -> content)

      stdin.println(write(msg))
      stdin.flush()

      val line = stdout.readLine()
      val rep = parse(line)

      rep \ "content"
    }
  }

  override def statement(id: Int): Option[JValue] = {
    if (id < _statements.length) {
      Some(_statements(id))
    } else {
      None
    }
  }

  override def close(): Unit = {
    process.getInputStream.close()
    process.getOutputStream.close()
    process.destroy()
  }
}
