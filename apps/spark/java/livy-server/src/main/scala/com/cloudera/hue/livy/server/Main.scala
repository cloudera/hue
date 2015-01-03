package com.cloudera.hue.livy.server

import javax.servlet.ServletContext

import scala.concurrent.duration._
import com.cloudera.hue.livy.WebServer
import org.json4s.{DefaultFormats, Formats}
import org.scalatra._
import org.scalatra.json.JacksonJsonSupport
import org.scalatra.servlet.ScalatraListener

import scala.concurrent.{Await, ExecutionContext, ExecutionContextExecutor}

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

  val getStatements = get("/sessions/:sessionId/statements") {
    sessionManager.get(params("sessionId")) match {
      case Some(session: Session) =>
        val statements = session.statements()
        val statementsWaited = Await.result(statements, Duration.Inf) //5 seconds)
        //new AsyncResult() { val is = statements }
        statementsWaited
      case None => NotFound("Session not found")
    }
  }

  val getSession = get("/sessions/:sessionId") {
    redirect(url(getStatements, "sessionId" -> params("sessionId")))
  }

  delete("/sessions/:sessionId") {
    sessionManager.close(params("sessionId"))
    NoContent
  }

  post("/sessions/:sessionId/statements") {
    val req = parsedBody.extract[ExecuteStatementRequest]

    sessionManager.get(params("sessionId")) match {
      case Some(session) =>
        val statement = session.executeStatement(req.statement)
        val foo = Await.result(statement, Duration.Inf)
        foo


        //new AsyncResult() { val is = statement }
      case None => NotFound("Session not found")
    }
  }

  val getStatement = get("/sessions/:sessionId/statements/:statementId") {
    sessionManager.get(params("sessionId")) match {
      case Some(session) =>
        val statement = session.statement(params("statementId").toInt)
        new AsyncResult() { val is = statement }
      case None => NotFound("Session not found")
    }
  }
}

case class CreateSessionRequest(lang: String)
case class ExecuteStatementRequest(statement: String)
