package com.cloudera.hue.livy.server

import com.cloudera.hue.livy.LivyConf
import com.cloudera.hue.livy.server.sessions.ProcessSession
import com.cloudera.hue.livy.sessions.Spark
import org.scalatest.{BeforeAndAfter, FunSpecLike, Matchers}

class ProcessSessionSpec extends BaseSessionSpec with FunSpecLike with Matchers with BeforeAndAfter {

  val livyConf = new LivyConf()
  livyConf.set("livy.repl.driverClassPath", sys.props("java.class.path"))

  def createSession() = ProcessSession.create(livyConf, "0", Spark())
}
