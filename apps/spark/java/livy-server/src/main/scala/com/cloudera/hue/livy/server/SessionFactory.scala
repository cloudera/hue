package com.cloudera.hue.livy.server

import java.util.UUID

import com.cloudera.hue.livy.LivyConf
import com.cloudera.hue.livy.server.sessions._
import com.cloudera.hue.livy.yarn.Client

import scala.concurrent.{ExecutionContext, Future}

trait SessionFactory {
  def createSession(lang: String): Future[Session]

  def close(): Unit = {}
}

class ThreadSessionFactory(livyConf: LivyConf) extends SessionFactory {

  implicit def executor: ExecutionContext = ExecutionContext.global

  override def createSession(lang: String): Future[Session] = {
    Future {
      val id = UUID.randomUUID().toString
      ThreadSession.create(id, lang)
    }
  }
}

class ProcessSessionFactory(livyConf: LivyConf) extends SessionFactory {

  implicit def executor: ExecutionContext = ExecutionContext.global

  override def createSession(lang: String): Future[Session] = {
    Future {
      val id = UUID.randomUUID().toString
      ProcessSession.create(id, lang)
    }
  }
}

class YarnSessionFactory(livyConf: LivyConf) extends SessionFactory {

  val client = new Client(livyConf)

  override def createSession(lang: String): Future[Session] = {
    val id = UUID.randomUUID().toString
    YarnSession.create(client, id, lang)
  }

  override def close(): Unit = {
    client.close()
  }
}
