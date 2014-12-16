import javax.servlet.ServletContext

import _root_.akka.actor.ActorSystem
import com.cloudera.hue.sparker.repl.interpreter.SparkerInterpreter
import com.cloudera.hue.sparker.repl.webapp.SparkerApp
import org.scalatra.LifeCycle

class ScalatraBootstrap extends LifeCycle {

  //val system = ActorSystem()
  val sparkerInterpreter = new SparkerInterpreter

  override def init(context: ServletContext): Unit = {
    context.mount(new SparkerApp(sparkerInterpreter), "/*")
  }

  override def destroy(context: ServletContext): Unit = {
    sparkerInterpreter.close()
    //system.shutdown()
  }
}
