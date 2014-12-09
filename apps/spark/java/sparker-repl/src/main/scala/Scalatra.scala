import javax.servlet.ServletContext

import org.eclipse.jetty.server.Server
import org.eclipse.jetty.servlet.DefaultServlet
import org.eclipse.jetty.webapp.WebAppContext
import org.scalatra.{ScalatraFilter, LifeCycle}
import org.scalatra.servlet.ScalatraListener

class HelloWorldApp extends ScalatraFilter {
  get("/") {
    <h1>Hello {params("name")}</h1>
  }
}

object Main {
  def main(args: Array[String]): Unit = {
    val port = 8087
    val server = new Server(port)
    val context = new WebAppContext()
    context.setContextPath("/")
    context.setResourceBase("src/main/com/cloudera/hue/sparker/repl")
    context.addEventListener(new ScalatraListener)
    context.addServlet(classOf[DefaultServlet], "/")

    server.setHandler(context)

    server.start()
    server.join()
  }
}

class ScalatraBootstrap extends LifeCycle {
  override def init(context: ServletContext): Unit = {
    context.mount(new HelloWorldApp, "/*")
  }
}
