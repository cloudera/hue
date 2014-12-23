package com.cloudera.hue.livy.repl

import javax.servlet.ServletContext

import com.cloudera.hue.livy.{Logging, WebServer}
import org.scalatra.LifeCycle
import org.scalatra.servlet.ScalatraListener

object Main extends Logging {
  def main(args: Array[String]): Unit = {
    val port = sys.env.getOrElse("PORT", "8999").toInt
    val server = new WebServer(port)

    server.context.setResourceBase("src/main/com/cloudera/hue/livy/repl")
    server.context.setInitParameter(ScalatraListener.LifeCycleKey, classOf[ScalatraBootstrap].getCanonicalName)
    server.context.addEventListener(new ScalatraListener)

    server.start()
    println("Starting livy-repl on port %s" format server.port)

    server.join()
    server.stop()
  }
}

class ScalatraBootstrap extends LifeCycle {

  //val system = ActorSystem()
  val sparkInterpreter = new SparkInterpreter

  override def init(context: ServletContext): Unit = {
    context.mount(new WebApp(sparkInterpreter), "/*")
  }

  override def destroy(context: ServletContext): Unit = {
    sparkInterpreter.close()
    //system.shutdown()
  }
}