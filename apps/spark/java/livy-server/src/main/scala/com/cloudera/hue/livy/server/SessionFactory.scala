package com.cloudera.hue.livy.server

import java.util.UUID

import scala.concurrent.{ExecutionContext, Future}

trait SessionFactory {
  def createSparkSession: Future[Session]
}

class ProcessSessionFactory extends SessionFactory {

  implicit def executor: ExecutionContext = ExecutionContext.global

  override def createSparkSession: Future[Session] = {
    Future {
      val id = UUID.randomUUID().toString
      SparkProcessSession.create(id)
    }
  }
}
