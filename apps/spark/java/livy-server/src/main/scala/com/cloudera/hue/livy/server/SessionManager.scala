package com.cloudera.hue.livy.server

import scala.collection.concurrent.TrieMap
import scala.concurrent.{ExecutionContext, ExecutionContextExecutor, Future}

object SessionManager {
  // Time in milliseconds; TODO: make configurable
  val TIMEOUT = 60000

  // Time in milliseconds; TODO: make configurable
  val GC_PERIOD = 1000 * 60 * 60
}

class SessionManager(factory: SessionFactory) {

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
    val session = factory.createSparkSession

    session.map({ case(session: Session) =>
        sessions.put(session.id, session)
        session
    })
  }

  def close(): Unit = {
    sessions.values.foreach(close)
    garbageCollector.shutdown()
  }

  def close(sessionId: String): Unit = {
    sessions.remove(sessionId) match {
      case Some(session) => session.close()
      case None =>
    }
  }

  def close(session: Session): Unit = {
    sessions.remove(session.id)
    session.close()
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
