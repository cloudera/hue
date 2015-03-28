package com.cloudera.hue.livy.server

import com.cloudera.hue.livy.LivyConf
import com.cloudera.hue.livy.server.sessions.{ProcessSession, Session}
import org.scalatest.matchers.ShouldMatchers
import org.scalatest.{Matchers, FunSpecLike, BeforeAndAfter, FunSpec}

class ProcessSessionSpec extends BaseSessionSpec with FunSpecLike with Matchers with BeforeAndAfter {

  val livyConf = new LivyConf()
  livyConf.set("livy.repl.driverClassPath", sys.props("java.class.path"))

  def createSession() = ProcessSession.create(livyConf, "0", Session.Spark())
}
