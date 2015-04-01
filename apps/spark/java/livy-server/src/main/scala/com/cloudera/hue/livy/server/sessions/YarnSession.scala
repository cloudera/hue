package com.cloudera.hue.livy.server.sessions

import java.util.concurrent.TimeUnit

import com.cloudera.hue.livy.sessions.{Kind, Error}
import com.cloudera.hue.livy.yarn.{Client, Job}

import scala.concurrent.{Await, ExecutionContext, ExecutionContextExecutor, Future}
import scala.concurrent.duration._

object YarnSession {
  protected implicit def executor: ExecutionContextExecutor = ExecutionContext.global

  def create(client: Client, id: String, kind: Kind, proxyUser: Option[String] = None): Future[Session] = {
    val callbackUrl = System.getProperty("livy.server.callback-url")
    val job = client.submitApplication(
      id = id,
      kind = kind.toString,
      proxyUser = proxyUser,
      callbackUrl = callbackUrl)

    Future.successful(new YarnSession(id, kind, proxyUser, job))
  }
}

private class YarnSession(id: String,
                          kind: Kind,
                          proxyUser: Option[String],
                          job: Future[Job]) extends WebSession(id, kind, proxyUser) {
  job.onFailure { case _ =>
    _state = Error()
  }

  override def stop(): Future[Unit] = {
    super.stop().andThen {
      case _ =>
        try {
          val job_ = Await.result(job, Duration(1, TimeUnit.SECONDS))
          job_.waitForFinish(10000)
        } catch {
          case e: Throwable =>
            _state = Error()
            throw e
        }
    }
  }
}
