package com.cloudera.hue.livy.repl

import javax.servlet.ServletContext

import com.cloudera.hue.livy.repl.python.PythonSession
import com.cloudera.hue.livy.repl.scala.ScalaSession
import com.cloudera.hue.livy.{Logging, WebServer}
import org.scalatra.LifeCycle
import org.scalatra.servlet.ScalatraListener

object Main extends Logging {

  val SESSION_KIND = "livy-repl.session.kind"
  val PYTHON_SESSION = "python"
  val SCALA_SESSION = "scala"

  def main(args: Array[String]): Unit = {
    val port = sys.env.getOrElse("PORT", "8999").toInt

    if (args.length != 1) {
      println("Must specify either `python` or `scala` for the session kind")
      sys.exit(1)
    }

    val session_kind = args(0)

    session_kind match {
      case PYTHON_SESSION | SCALA_SESSION =>
      case _ =>
        println("Unknown session kind: " + session_kind)
        sys.exit(1)
    }

    val server = new WebServer(port)

    server.context.setResourceBase("src/main/com/cloudera/hue/livy/repl")
    server.context.setInitParameter(ScalatraListener.LifeCycleKey, classOf[ScalatraBootstrap].getCanonicalName)
    server.context.addEventListener(new ScalatraListener)
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
      case Main.PYTHON_SESSION => PythonSession.create()
      case Main.SCALA_SESSION => ScalaSession.create()
    }

    context.mount(new WebApp(session), "/*")
  }

  override def destroy(context: ServletContext): Unit = {
    session.close()
  }
}