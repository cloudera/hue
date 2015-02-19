package com.cloudera.hue.livy.server.sessions

import com.cloudera.hue.livy.yarn.{Client, Job}

import scala.concurrent.{Await, ExecutionContext, ExecutionContextExecutor, Future}
import scala.concurrent.duration._

object YarnSession {
  protected implicit def executor: ExecutionContextExecutor = ExecutionContext.global

  def create(client: Client, id: String, lang: String): Future[Session] = {
    val callbackUrl = System.getProperty("livy.server.callback-url")
    val job = client.submitApplication(id, lang, callbackUrl)

    Future.successful(new YarnSession(id, job))
  }
}

private class YarnSession(id: String, job: Future[Job]) extends WebSession(id) {
  job.onFailure { case _ =>
    _state = Session.Error()
  }

  override def stop(): Future[Unit] = {
    super.stop().andThen {
      case _ =>
        try {
          val job_ = Await.result(job, 1 second)
          job_.waitForFinish(10000)
        } catch {
          case e: Throwable =>
            _state = Session.Error()
            throw e
        }
    }
  }
}
