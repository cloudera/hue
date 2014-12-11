import javax.servlet.ServletContext

import akka.actor.{ActorSystem, Props}
import com.cloudera.hue.sparker.repl.{HelloWorldApp, SparkActor}
import org.scalatra.LifeCycle

trait SparkerILoopInit {
  def configureSparkerILoop() {
    /*
    org.apache.spark.repl.Main.interp = new SparkerILoop(Console.in, new StringWriter)

    val args = Array("-usejavacp")
    org.apache.spark.repl.Main.interp.process(args)
    */
  }
}

class ScalatraBootstrap extends LifeCycle with SparkerILoopInit {

  val system = ActorSystem()

  override def init(context: ServletContext): Unit = {
    val myActor = system.actorOf(Props[SparkActor])

    configureSparkerILoop()
    context.mount(new HelloWorldApp(system, myActor), "/*")
  }

  override def destroy(context: ServletContext): Unit = {
    system.shutdown()
  }
}
