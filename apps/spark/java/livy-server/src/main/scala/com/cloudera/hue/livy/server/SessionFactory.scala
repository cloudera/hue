package com.cloudera.hue.livy.server

import java.util.UUID

import com.cloudera.hue.livy.server.sessions.{Session, SparkYarnSession, SparkProcessSession}
import com.cloudera.hue.livy.yarn.Client
import org.apache.hadoop.yarn.conf.YarnConfiguration

import scala.concurrent.{ExecutionContext, Future}

trait SessionFactory {
  def createSparkSession(): Future[Session]

  def close(): Unit = {}
}

class ProcessSessionFactory extends SessionFactory {

  implicit def executor: ExecutionContext = ExecutionContext.global

  override def createSparkSession(): Future[Session] = {
    Future {
      val id = UUID.randomUUID().toString
      SparkProcessSession.create(id)
    }
  }
}

class YarnSessionFactory extends SessionFactory {

  val yarnConf = new YarnConfiguration()
  yarnConf.set("yarn.resourcemanager.am.max-attempts", "1")

  val client = new Client(yarnConf)

  override def createSparkSession(): Future[Session] = {
    val id = UUID.randomUUID().toString
    SparkYarnSession.create(client, id)
  }

  override def close(): Unit = {
    client.close()
  }
}