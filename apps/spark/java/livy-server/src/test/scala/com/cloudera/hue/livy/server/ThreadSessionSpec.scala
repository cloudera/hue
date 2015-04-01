package com.cloudera.hue.livy.server

import com.cloudera.hue.livy.server.sessions.ThreadSession
import com.cloudera.hue.livy.sessions.Spark
import org.scalatest.{BeforeAndAfter, FunSpecLike, Matchers}

class ThreadSessionSpec extends BaseSessionSpec with FunSpecLike with Matchers with BeforeAndAfter {

  def createSession() = ThreadSession.create("0", Spark())
}
