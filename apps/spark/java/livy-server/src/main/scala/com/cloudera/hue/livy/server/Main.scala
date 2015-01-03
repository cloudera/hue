package com.cloudera.hue.livy.server

import javax.servlet.ServletContext

import _root_.akka.util.Timeout
import com.cloudera.hue.livy.WebServer
import org.json4s.{DefaultFormats, Formats}
import org.scalatra._
import org.scalatra.json.JacksonJsonSupport
import org.scalatra.servlet.ScalatraListener

import scala.concurrent.{ExecutionContext, ExecutionContextExecutor}

object Main {
  def main(args: Array[String]): Unit = {
    val port = sys.env.getOrElse("PORT", "8998").toInt
    val server = new WebServer(port)

    server.context.setResourceBase("src/main/com/cloudera/hue/livy/server")
    server.context.setInitParameter(ScalatraListener.LifeCycleKey, classOf[ScalatraBootstrap].getCanonicalName)
    server.context.addEventListener(new ScalatraListener)

    server.start()
    server.join()
    server.stop()
  }
}

class ScalatraBootstrap extends LifeCycle {

  val sessionFactory = new ProcessSessionFactory
  val sessionManager = new SessionManager(sessionFactory)

  override def init(context: ServletContext): Unit = {
    context.mount(new WebApp(sessionManager), "/*")
  }

  override def destroy(context: ServletContext): Unit = {
    sessionManager.close()
  }
}

class WebApp(sessionManager: SessionManager) extends ScalatraServlet with FutureSupport with MethodOverride with JacksonJsonSupport with UrlGeneratorSupport {

  override protected implicit def executor: ExecutionContextExecutor = ExecutionContext.global
  override protected implicit def jsonFormats: Formats = DefaultFormats

  protected implicit def defaultTimeout: Timeout = Timeout(10)

  before() {
    contentType = formats("json")
  }

  get("/sessions") {
    sessionManager.getSessionIds
  }

  post("/sessions") {
    val createSessionRequest = parsedBody.extract[CreateSessionRequest]

    val sessionFuture = createSessionRequest.lang match {
      case "scala" => sessionManager.createSparkSession()
      case lang => halt(400, "unsupported language: " + lang)
    }

    val rep = for {
      session <- sessionFuture
    } yield redirect(url(getSession, "sessionId" -> session.id))

    new AsyncResult { val is = rep }
  }

  val getSession = get("/sessions/:sessionId") {
    sessionManager.get(params("sessionId"))
  }

  delete("/sessions/:sessionId") {
    sessionManager.close(params("sessionId"))
    NoContent
  }

  get("/sessions/:sessionId/statements") {
    val rep = sessionManager.get(params("sessionId")) match {
      case Some(session) => session.statements()
      case None => NotFound
    }

    new AsyncResult() { val is = rep }
  }

  post("/sessions/:sessionId/statements") {
    val req = parsedBody.extract[ExecuteStatementRequest]

    val rep = sessionManager.get(params("sessionId")) match {
      case Some(session) => session.executeStatement(req.statement)
      case None => NotFound
    }

    new AsyncResult() { val is = rep }
  }

  val getStatement = get("/sessions/:sessionId/statements/:statementId") {
    val rep = sessionManager.get(params("sessionId")) match {
      case Some(session) => session.statement(params("statementId").toInt)
      case None => NotFound
    }

    new AsyncResult() { val is = rep }
  }
}

case class CreateSessionRequest(lang: String)
case class ExecuteStatementRequest(statement: String)
