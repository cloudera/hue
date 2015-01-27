package com.cloudera.hue.livy.repl.python

import java.io._

import com.cloudera.hue.livy.ExecuteResponse
import com.cloudera.hue.livy.repl.Session
import org.json4s.DefaultFormats
import org.json4s.JsonAST._
import org.json4s.JsonDSL._
import org.json4s.jackson.JsonMethods._

import scala.collection.mutable.ArrayBuffer
import scala.concurrent.{ExecutionContext, Future}

object PythonSession {
  val LIVY_HOME = System.getenv("LIVY_HOME")
  val FAKE_SHELL = LIVY_HOME + "/livy-repl/src/main/python/fake_shell.py"

  def create(): Session = {
    val pb = new ProcessBuilder("python", FAKE_SHELL)
    val process = pb.start()
    val in = process.getInputStream
    val out = process.getOutputStream

    new PythonSession(process, in, out)
  }

  // Java unfortunately wraps the input stream in a buffer, so we need to hack around it so we can read the output
  // without blocking.
  private def unwrapInputStream(inputStream: InputStream) = {
    var filteredInputStream = inputStream

    while (filteredInputStream.isInstanceOf[FilterInputStream]) {
      val field = classOf[FilterInputStream].getDeclaredField("in")
      field.setAccessible(true)
      filteredInputStream = field.get(filteredInputStream).asInstanceOf[InputStream]
    }

    filteredInputStream
  }

  // Java unfortunately wraps the output stream in a buffer, so we need to hack around it so we can read the output
  // without blocking.
  private def unwrapOutputStream(outputStream: OutputStream) = {
    var filteredOutputStream = outputStream

    while (filteredOutputStream.isInstanceOf[FilterOutputStream]) {
      val field = classOf[FilterOutputStream].getDeclaredField("out")
      field.setAccessible(true)
      filteredOutputStream = field.get(filteredOutputStream).asInstanceOf[OutputStream]
    }

    filteredOutputStream
  }
}

private class PythonSession(process: Process, in: InputStream, out: OutputStream) extends Session {
  private implicit def executor: ExecutionContext = ExecutionContext.global

  implicit val formats = DefaultFormats

  private[this] val stdin = new PrintWriter(out)
  private[this] val stdout = new BufferedReader(new InputStreamReader(in), 1)

  private[this] var executedStatements = 0
  private[this] var _statements = ArrayBuffer[ExecuteResponse]()

  override def statements: Seq[ExecuteResponse] = _statements

  override def execute(command: String): Future[ExecuteResponse] = {
    val request = Map(
      "msg_type" -> "execute_request",
      "code" -> command
    )

    stdin.println(compact(render(request)))
    stdin.flush()

    val line = stdout.readLine()

    val response = parse(line)

    val content = response \ "content"
    val status = (content\ "status").extract[String]
    val executionCount = (content \ "execution_count").extract[Int]

    val executeResponse = status match {
      case "ok" =>
        val output = (content \ "data" \ "text/plain").extract[String]
        ExecuteResponse(executionCount, Seq(command), Seq(output))
      case "error" =>
        val ename = (content \ "ename").extract[String]
        val evalue = (content \ "evalue").extract[String]
        val traceback = (content \ "traceback").extract[Seq[String]]

        val output = traceback :+ ("%s: %s" format(ename, evalue))

        ExecuteResponse(executionCount, Seq(command), output)
    }

    Future.successful(executeResponse)

    /*
    val response = ExecuteResponse(executedStatements - 1, Seq(command), output)
    _statements += response

    executedStatements += 1

    Future.successful(response)
    */
  }

  override def statement(id: Int): Option[ExecuteResponse] = {
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
    /*
    if (!process.waitFor(10l, TimeUnit.SECONDS)) {
      process.destroyForcibly()
      process.waitFor()
    }
    */
  }


  /*
  private def readLines(): Seq[String] = {
    var sb = new StringBuilder
    var output = new ArrayBuffer[String]()

    @tailrec
    def aux(): Unit = {
      stdout.


      val line = stdout.readLine()
      if (line != null && !line.startsWith(">>> ") && !line.startsWith("... ")) {
        output += line
        aux()
      }
    }

    aux()

    output

    /*
    val output = stdout.takeWhile({
      case line: String =>
        println(line)
        line.startsWith(">>> ") || line.startsWith("... ")
    }).toSeq
    */
  }
  */
}
