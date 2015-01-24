package com.cloudera.hue.livy.server

import com.cloudera.hue.livy.Logging

import scala.collection.concurrent.TrieMap
import scala.concurrent.duration.Duration
import scala.concurrent.{Await, ExecutionContext, ExecutionContextExecutor, Future}

object SessionManager {
  // Time in milliseconds; TODO: make configurable
  val TIMEOUT = 60000

  // Time in milliseconds; TODO: make configurable
  val GC_PERIOD = 1000 * 60 * 60
}

class SessionManager(factory: SessionFactory) extends Logging {

  private implicit def executor: ExecutionContextExecutor = ExecutionContext.global

  private val sessions = new TrieMap[String, Session]()

  private val garbageCollector = new GarbageCollector(this)
  garbageCollector.start()

  def get(id: String): Option[Session] = {
    sessions.get(id)
  }

  def getSessionIds = {
    sessions.keys
  }

  def createSparkSession(): Future[Session] = {
    val session = factory.createSparkSession()

    session.map({ case(session: Session) =>
      info("created session %s" format session.id)
      sessions.put(session.id, session)
      session
    })
  }

  def close(): Unit = {
    Await.result(Future.sequence(sessions.values.map(close)), Duration.Inf)
    garbageCollector.shutdown()
  }

  def close(sessionId: String): Future[Unit] = {
    sessions.get(sessionId) match {
      case Some(session) => close(session)
      case None => Future.successful(Unit)
    }
  }

  def close(session: Session): Future[Unit] = {
    session.close().map { case _ =>
        sessions.remove(session.id)
        Unit
    }
  }

  def collectGarbage() = {
    def expired(session: Session): Boolean = {
      System.currentTimeMillis() - session.lastActivity > SessionManager.TIMEOUT
    }

    sessions.values.filter(expired).foreach(close)
  }
}

class SessionNotFound extends Exception

private class GarbageCollector(sessionManager: SessionManager) extends Thread {

  private var finished = false

  override def run(): Unit = {
    while (!finished) {
      sessionManager.collectGarbage()
      Thread.sleep(SessionManager.GC_PERIOD)
    }
  }

  def shutdown(): Unit = {
    finished = true
  }
}
