package com.cloudera.hue.livy.server

import java.util.UUID
import java.util.concurrent.Executors

import com.cloudera.hue.livy.server.sessions.{Session, SparkSession}

import scala.concurrent.{ExecutionContext, Future, future}

trait SessionFactory {
  def createSparkSession: Future[Session]
}

class ProcessSessionFactory extends SessionFactory {

  implicit def executor: ExecutionContext = ExecutionContext.global //ExecutionContext.fromExecutor(Executors.newFixedThreadPool(5))

  override def createSparkSession: Future[Session] = {
    future {
      val id = UUID.randomUUID().toString
      new SparkSession(id)
    }
  }
}
