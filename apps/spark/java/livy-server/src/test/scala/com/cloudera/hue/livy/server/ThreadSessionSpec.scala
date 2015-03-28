package com.cloudera.hue.livy.server

import com.cloudera.hue.livy.server.sessions.{Session, ThreadSession}
import org.scalatest.{BeforeAndAfter, FunSpecLike, Matchers}

class ThreadSessionSpec extends BaseSessionSpec with FunSpecLike with Matchers with BeforeAndAfter {

  def createSession() = ThreadSession.create("0", Session.Spark())
}
