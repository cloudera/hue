package com.cloudera.hue.livy.repl

import javax.servlet.ServletContext

import com.cloudera.hue.livy.repl.python.PythonSession
import com.cloudera.hue.livy.repl.scala.SparkSession
import com.cloudera.hue.livy.{Logging, WebServer}
import org.scalatra.LifeCycle
import org.scalatra.servlet.ScalatraListener

object Main extends Logging {

  val SESSION_KIND = "livy-repl.session.kind"
  val PYTHON_SESSION = "python"
  val PYSPARK_SESSION = "pyspark"
  val SCALA_SESSION = "scala"
  val SPARK_SESSION = "spark"

  def main(args: Array[String]): Unit = {
    val port = sys.env.getOrElse("PORT", "8999").toInt

    if (args.length != 1) {
      println("Must specify either `python`/`pyspark`/`scala/`spark` for the session kind")
      sys.exit(1)
    }

    val session_kind = args(0)

    session_kind match {
      case PYTHON_SESSION | PYSPARK_SESSION | SPARK_SESSION =>
      case _ =>
        println("Unknown session kind: " + session_kind)
        sys.exit(1)
    }

    val server = new WebServer(port)

    server.context.setResourceBase("src/main/com/cloudera/hue/livy/repl")
    server.context.addEventListener(new ScalatraListener)
    server.context.setInitParameter(ScalatraListener.LifeCycleKey, classOf[ScalatraBootstrap].getCanonicalName)
    server.context.setInitParameter(SESSION_KIND, session_kind)

    server.start()
    println("Starting livy-repl on port %s" format server.port)

    server.join()
    server.stop()
  }
}

class ScalatraBootstrap extends LifeCycle {

  var session: Session = null

  override def init(context: ServletContext): Unit = {
    val session = context.getInitParameter(Main.SESSION_KIND) match {
      case Main.PYTHON_SESSION => PythonSession.createPySpark()
      case Main.PYSPARK_SESSION => PythonSession.createPySpark()
      case Main.SCALA_SESSION => SparkSession.create()
      case Main.SPARK_SESSION => SparkSession.create()
    }

    context.mount(new WebApp(session), "/*")
  }

  override def destroy(context: ServletContext): Unit = {
    session.close()
  }
}