package com.cloudera.hue.livy.spark

import com.cloudera.hue.livy.LivyConf
import com.cloudera.hue.livy.LivyConf.{Process, Yarn}
import com.cloudera.hue.livy.sessions.SessionManager
import com.cloudera.hue.livy.sessions.batch.BatchSession
import com.cloudera.hue.livy.sessions.interactive.InteractiveSession
import com.cloudera.hue.livy.spark.batch.{BatchSessionProcessFactory, BatchSessionYarnFactory}
import com.cloudera.hue.livy.spark.interactive.{InteractiveSessionProcessFactory, InteractiveSessionYarnFactory}
import com.cloudera.hue.livy.yarn.Client

object SparkManager {
  def apply(livyConf: LivyConf): SparkManager = {
    val processFactory = SparkProcessBuilderFactory(livyConf)

    livyConf.sessionKind() match {
      case Process() => new SparkProcessManager(processFactory)
      case Yarn() => new SparkYarnManager(processFactory)
    }
  }
}

trait SparkManager {
  def batchManager: SessionManager[BatchSession]

  def interactiveManager: SessionManager[InteractiveSession]

  def shutdown()
}

private class SparkProcessManager(processFactory: SparkProcessBuilderFactory) extends SparkManager {
  private[this] val batchFactory = new BatchSessionProcessFactory(processFactory)
  private[this] val interactiveFactory = new InteractiveSessionProcessFactory(processFactory)

  val batchManager = new SessionManager(processFactory.livyConf, batchFactory)

  val interactiveManager = new SessionManager(processFactory.livyConf, interactiveFactory)

  override def shutdown(): Unit = {
    batchManager.shutdown()
    interactiveManager.shutdown()
  }
}

private class SparkYarnManager(processFactory: SparkProcessBuilderFactory) extends SparkManager {
  private[this] val client = new Client(processFactory.livyConf)
  private[this] val batchFactory = new BatchSessionYarnFactory(client, processFactory)
  private[this] val interactiveFactory = new InteractiveSessionYarnFactory(client, processFactory)

  val batchManager = new SessionManager(processFactory.livyConf, batchFactory)

  val interactiveManager = new SessionManager(processFactory.livyConf, interactiveFactory)

  override def shutdown(): Unit = {
    batchManager.shutdown()
    interactiveManager.shutdown()
    client.close()
  }
}