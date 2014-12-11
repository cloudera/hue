package com.cloudera.hue.sparker.repl

import java.io._
import java.util.concurrent.{ArrayBlockingQueue, SynchronousQueue, TimeUnit}

import akka.actor.{Actor, ActorRef, ActorSystem}
import akka.pattern.ask
import akka.util.Timeout
import org.json4s.JsonDSL._
import org.json4s.jackson.JsonMethods._
import org.scalatra.{Accepted, FutureSupport, ScalatraFilter}

import scala.concurrent.duration.Duration
import scala.concurrent.{Await, ExecutionContext}

class HelloWorldApp(system: ActorSystem, sparkActor: ActorRef) extends ScalatraFilter with FutureSupport {

  protected implicit def executor: ExecutionContext = system.dispatcher

  implicit val defaultTimeout = Timeout(10)

  get("/") {
    <h1>Hello {params("name")}</h1>
  }

  get("/async") {
    val future = ask(sparkActor, "1 + 1")

    implicit val timeout = akka.util.Timeout(60, TimeUnit.SECONDS)
    Await.result(future, Duration.Inf)
  }

  get("/fire-forget") {
    sparkActor ! "wee"
    Accepted()
  }
}

class SparkActor extends Actor {

  protected def queue = new SynchronousQueue[Map[String, String]]

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
