import javax.servlet.ServletContext

import com.cloudera.hue.livy.yarn.WebApp
import org.scalatra.LifeCycle

class ScalatraBootstrap extends LifeCycle {

  override def init(context: ServletContext): Unit = {
    context.mount(new WebApp, "/*")
  }

  override def destroy(context: ServletContext): Unit = {
  }
}
