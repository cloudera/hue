package com.cloudera.hue.livy.server

import java.util.UUID

import com.cloudera.hue.livy.LivyConf
import com.cloudera.hue.livy.server.sessions._
import com.cloudera.hue.livy.yarn.Client

import scala.concurrent.{ExecutionContext, Future}

trait SessionFactory {
  def createSession(kind: Session.Kind, proxyUser: Option[String] = None): Future[Session]

  def close(): Unit = {}
}

class ThreadSessionFactory(livyConf: LivyConf) extends SessionFactory {

  implicit def executor: ExecutionContext = ExecutionContext.global

  override def createSession(kind: Session.Kind, proxyUser: Option[String] = None): Future[Session] = {
    Future {
      val id = UUID.randomUUID().toString
      ThreadSession.create(id, kind)
    }
  }
}

class ProcessSessionFactory(livyConf: LivyConf) extends SessionFactory {

  implicit def executor: ExecutionContext = ExecutionContext.global

  override def createSession(kind: Session.Kind, proxyUser: Option[String] = None): Future[Session] = {
    Future {
      val id = UUID.randomUUID().toString
      ProcessSession.create(livyConf, id, kind, proxyUser)
    }
  }
}

class YarnSessionFactory(livyConf: LivyConf) extends SessionFactory {

  val client = new Client(livyConf)

  override def createSession(kind: Session.Kind, proxyUser: Option[String] = None): Future[Session] = {
    val id = UUID.randomUUID().toString
    YarnSession.create(client, id, kind, proxyUser)
  }

  override def close(): Unit = {
    client.close()
  }
}
