package com.cloudera.hue.sparker.repl.webapp

import akka.util.Timeout
import com.cloudera.hue.sparker.repl.interpreter.SparkerInterpreter
import org.json4s.{DefaultFormats, Formats}
import org.scalatra.json._
import org.scalatra.{AsyncResult, FutureSupport, ScalatraServlet}

import scala.concurrent.{ExecutionContext, ExecutionContextExecutor}

class HelloWorldApp(interpreter: SparkerInterpreter) extends ScalatraServlet with FutureSupport with JacksonJsonSupport {

  protected implicit def executor: ExecutionContextExecutor = ExecutionContext.global
  protected implicit def defaultTimeout: Timeout = Timeout(10)
  protected implicit val jsonFormats: Formats = DefaultFormats

  before() {
    contentType = formats("json")
  }

  get("/") {
    <h1>Hello {params("name")}</h1>
  }

  post("/statement") {
    val req = parsedBody.extract[ExecuteRequest]
    val statement = req.statement
    new AsyncResult { val is = interpreter.execute(statement) }
  }
}

case class ExecuteRequest(statement: String)

/*
class SparkActor extends Actor {

  val queue = new SynchronousQueue[Map[String, String]]

  val inWriter = new PipedWriter()
  val inReader = new PipedReader(inWriter)

  /*
  protected def inWriter = new PipedWriter()
  protected def inReader = new PipedReader(inWriter)
  */

  protected def out = new StringWriter

  val thread = new Thread {
    override def run(): Unit = {
      org.apache.spark.repl.Main.interp = new SparkerILoop(
        queue,
        new BufferedReader(inReader),
        out)
      val args = Array("-usejavacp")
      org.apache.spark.repl.Main.interp.process(args)
    }
  }
  thread.start()

  def receive = {
    case msg : String => {
      inWriter.write(msg)
      val response = queue.take()
      val s = compact(render(response))
      sender ! s
    }
  }
}
*/
