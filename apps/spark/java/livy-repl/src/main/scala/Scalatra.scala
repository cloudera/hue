import javax.servlet.ServletContext

import com.cloudera.hue.livy.repl.interpreter.SparkInterpreter
import com.cloudera.hue.livy.repl.webapp.LivyApp
import org.scalatra.LifeCycle

class ScalatraBootstrap extends LifeCycle {

  //val system = ActorSystem()
  val sparkInterpreter = new SparkInterpreter

  override def init(context: ServletContext): Unit = {
    context.mount(new LivyApp(sparkInterpreter), "/*")
  }

  override def destroy(context: ServletContext): Unit = {
    sparkInterpreter.close()
    //system.shutdown()
  }
}
