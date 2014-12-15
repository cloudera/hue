package com.cloudera.hue.sparker.repl

import java.io._
import java.util.concurrent.SynchronousQueue

import akka.actor.{Actor, ActorSystem}
import akka.util.Timeout
import org.json4s.JsonDSL._
import org.json4s.jackson.JsonMethods._
import org.scalatra.{ScalatraServlet, AsyncResult, FutureSupport, ScalatraFilter}

import scala.concurrent.{ExecutionContextExecutor, ExecutionContext}

class HelloWorldApp(interpreter: SparkerInterpreter) extends ScalatraServlet with FutureSupport {

  implicit def executor: ExecutionContextExecutor = ExecutionContext.global
  implicit def defaultTimeout: Timeout = Timeout(10)

  get("/") {
    <h1>Hello {params("name")}</h1>
  }

  get("/async") {
    new AsyncResult { val is =
      interpreter.execute("1 + 1")
    }
  }

  /*
  get("/fire-forget") {
    sparkActor ! "wee"
    Accepted()
  }
  */
}

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
