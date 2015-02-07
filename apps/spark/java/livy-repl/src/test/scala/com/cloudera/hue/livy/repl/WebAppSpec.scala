package com.cloudera.hue.livy.repl

import com.cloudera.hue.livy.repl.Session.State
import org.json4s.JsonAST.{JArray, JString}
import org.json4s.JsonDSL._
import org.json4s.jackson.JsonMethods._
import org.json4s.{DefaultFormats, Extraction, JValue}
import org.scalatest.{BeforeAndAfter, FunSpec}
import org.scalatra.test.scalatest.ScalatraSuite
import _root_.scala.concurrent.Future

class WebAppSpec extends ScalatraSuite with FunSpec with BeforeAndAfter {

  implicit val formats = DefaultFormats

  class MockSession extends Session {
    var _state: State = Session.Idle()
    var _history = List[JValue]()

    override def state = _state

    override def execute(code: String): Future[JValue] = {
      val rep = render(Map("hi" -> "there"))
      Future.successful(rep)
    }

    override def close(): Future[Unit] = {
      _state = Session.ShuttingDown()
      Future.successful(())
    }

    override def history(): Seq[JValue] = _history

    override def history(id: Int): Option[JValue] = _history.lift(id)
  }

  val session = new MockSession
  val servlet = new WebApp(session)

  addServlet(servlet, "/*")

  describe("A session") {
    it("GET / should return the session state") {
      get("/") {
        status should equal (200)
        header("Content-Type") should include("application/json")
        val parsedBody = parse(body)
        parsedBody \ "state" should equal (JString("idle"))
      }

      session._state = Session.Busy()

      get("/") {
        status should equal (200)
        header("Content-Type") should include("application/json")
        val parsedBody = parse(body)
        parsedBody \ "state" should equal (JString("busy"))
      }
    }

    it("GET /history with no history should be empty") {
      get("/history") {
        status should equal (200)
        header("Content-Type") should include("application/json")
        parse(body) should equal (JArray(List()))
      }
    }

    it("GET /history with history should return something") {
      val history = Extraction.decompose(Map("data" -> Map("text/plain" -> "1")))
      session._history = List(history)

      get("/history") {
        status should equal (200)
        header("Content-Type") should include("application/json")
        parse(body) should equal (JArray(List(history)))
      }
    }
  }

  after {
    session._state = Session.Idle()
    session._history = List()
  }
}
