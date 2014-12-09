import java.io.StringWriter
import javax.servlet.ServletContext

import com.cloudera.hue.sparker.repl.{HelloWorldApp, SparkerILoop}
import org.scalatra.LifeCycle

trait SparkerILoopInit {
  def configureSparkerILoop() {
    org.apache.spark.repl.Main.interp = new SparkerILoop(Console.in, new StringWriter)
    org.apache.spark.repl.Main.interp.process(new Array[String](0))
  }
}

class ScalatraBootstrap extends LifeCycle with SparkerILoopInit {
  override def init(context: ServletContext): Unit = {
    configureSparkerILoop()
    context.mount(new HelloWorldApp, "/*")
  }
}
