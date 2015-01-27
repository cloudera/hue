package com.cloudera.hue.livy.server

import java.util.UUID

import com.cloudera.hue.livy.server.sessions._
import com.cloudera.hue.livy.yarn.Client
import org.apache.hadoop.yarn.conf.YarnConfiguration

import scala.concurrent.{ExecutionContext, Future}

trait SessionFactory {
  def createSession(lang: String): Future[Session]

  def close(): Unit = {}
}

class ProcessSessionFactory extends SessionFactory {

  implicit def executor: ExecutionContext = ExecutionContext.global

  override def createSession(lang: String): Future[Session] = {
    Future {
      val id = UUID.randomUUID().toString
      ProcessSession.create(id, lang)
    }
  }
}

class YarnSessionFactory extends SessionFactory {

  val yarnConf = new YarnConfiguration()
  yarnConf.set("yarn.resourcemanager.am.max-attempts", "1")

  val client = new Client(yarnConf)

  override def createSession(lang: String): Future[Session] = {
    val id = UUID.randomUUID().toString
    YarnSession.create(client, id, lang)
  }

  override def close(): Unit = {
    client.close()
  }
}