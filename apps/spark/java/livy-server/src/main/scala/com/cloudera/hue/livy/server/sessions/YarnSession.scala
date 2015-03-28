package com.cloudera.hue.livy.server.sessions

import java.util.concurrent.TimeUnit

import com.cloudera.hue.livy.yarn.{Client, Job}

import scala.concurrent.{Await, ExecutionContext, ExecutionContextExecutor, Future}
import scala.concurrent.duration._

object YarnSession {
  protected implicit def executor: ExecutionContextExecutor = ExecutionContext.global

  def create(client: Client, id: String, kind: Session.Kind): Future[Session] = {
    val callbackUrl = System.getProperty("livy.server.callback-url")
    val job = client.submitApplication(id, kind.toString, callbackUrl)

    Future.successful(new YarnSession(id, kind, job))
  }
}

private class YarnSession(id: String, kind: Session.Kind, job: Future[Job]) extends WebSession(id, kind) {
  job.onFailure { case _ =>
    _state = Session.Error()
  }

  override def stop(): Future[Unit] = {
    super.stop().andThen {
      case _ =>
        try {
          val job_ = Await.result(job, Duration(1, TimeUnit.SECONDS))
          job_.waitForFinish(10000)
        } catch {
          case e: Throwable =>
            _state = Session.Error()
            throw e
        }
    }
  }
}
