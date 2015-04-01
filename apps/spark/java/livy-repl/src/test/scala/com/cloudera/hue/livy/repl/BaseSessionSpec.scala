package com.cloudera.hue.livy.repl

import java.util.concurrent.TimeUnit

import com.cloudera.hue.livy.sessions.{Idle, Starting}
import org.json4s.DefaultFormats
import org.scalatest.{Matchers, FunSpec, BeforeAndAfter}

import _root_.scala.concurrent.duration.Duration

abstract class BaseSessionSpec extends FunSpec with Matchers with BeforeAndAfter {

  implicit val formats = DefaultFormats

  def createSession(): Session

  var session: Session = null

  before {
    session = createSession()
  }

  after {
    session.close()
  }

  describe("A session") {
    it("should start in the starting or idle state") {
      session.state should (equal (Starting()) or equal (Idle()))
    }

    it("should eventually become the idle state") {
      session.waitForStateChange(Starting(), Duration(10, TimeUnit.SECONDS))
      session.state should equal (Idle())
    }
  }
}
