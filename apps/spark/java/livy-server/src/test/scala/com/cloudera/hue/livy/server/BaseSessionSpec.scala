package com.cloudera.hue.livy.server

import java.util.concurrent.TimeUnit

import com.cloudera.hue.livy.msgs.ExecuteRequest
import com.cloudera.hue.livy.server.sessions.Session
import org.json4s.{DefaultFormats, Extraction}
import org.scalatest.matchers.ShouldMatchers
import org.scalatest.{BeforeAndAfter, FunSpec}

import scala.concurrent.Await
import scala.concurrent.duration.Duration

abstract class BaseSessionSpec extends FunSpec with ShouldMatchers with BeforeAndAfter {

  implicit val formats = DefaultFormats

  var session: Session = null

  def createSession(): Session

  before {
    session = createSession()
  }

  after {
    session.stop()
  }

  describe("A spark session") {
    it("should start in the starting or idle state") {
      session.state should (equal (Session.Starting()) or equal (Session.Idle()))
    }

    it("should eventually become the idle state") {
      session.waitForStateChange(Session.Starting(), Duration(30, TimeUnit.SECONDS))
      session.state should equal (Session.Idle())
    }

    it("should execute `1 + 2` == 3") {
      session.waitForStateChange(Session.Starting(), Duration(30, TimeUnit.SECONDS))
      val stmt = session.executeStatement(ExecuteRequest("1 + 2"))
      val result = Await.result(stmt.output, Duration.Inf)

      val expectedResult = Extraction.decompose(Map(
        "status" -> "ok",
        "execution_count" -> 0,
        "data" -> Map(
          "text/plain" -> "res0: Int = 3"
        )
      ))

      result should equal (expectedResult)
    }

    it("should report an error if accessing an unknown variable") {
      session.waitForStateChange(Session.Starting(), Duration(30, TimeUnit.SECONDS))
      val stmt = session.executeStatement(ExecuteRequest("x"))
      val result = Await.result(stmt.output, Duration.Inf)
      val expectedResult = Extraction.decompose(Map(
        "status" -> "error",
        "execution_count" -> 0,
        "ename" -> "Error",
        "evalue" ->
          """<console>:8: error: not found: value x
            |              x
            |              ^""".stripMargin
      ))

      result should equal (expectedResult)
    }
  }
}
