package com.cloudera.hue.livy.server.batch

import java.lang.ProcessBuilder.Redirect
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.atomic.AtomicInteger

import com.cloudera.hue.livy.LineBufferedProcess
import com.cloudera.hue.livy.spark.SparkSubmitProcessBuilder

import scala.collection.JavaConversions._
import scala.concurrent.{ExecutionContext, ExecutionContextExecutor, Future}

class BatchManager(batchFactory: BatchFactory) {
  private[this] val _idCounter = new AtomicInteger()
  private[this] val _batches = new ConcurrentHashMap[Int, Batch]

  def getBatch(id: Int): Option[Batch] = Option(_batches.get(id))

  def getBatches: Array[Batch] = _batches.values().iterator().toArray

  def createBatch(createBatchRequest: CreateBatchRequest): Batch = {
    val id = _idCounter.getAndIncrement
    val batch = batchFactory.createBatch(id, createBatchRequest)
    _batches.put(id, batch)

    batch
  }

  def remove(id: Int): Option[Batch] = {
    Option(_batches.remove(id))
  }

  def delete(batch: Batch): Future[Unit] = {
    _batches.remove(batch.id)
    batch.stop()
  }

  def shutdown() = {

  }
}

case class CreateBatchRequest(file: String,
                              args: List[String] = List(),
                              className: Option[String] = None,
                              jars: List[String] = List(),
                              pyFiles: List[String] = List(),
                              files: List[String] = List(),
                              driverMemory: Option[String] = None,
                              driverCores: Option[Int] = None,
                              executorMemory: Option[String] = None,
                              executorCores: Option[Int] = None,
                              archives: List[String] = List())

abstract class BatchFactory {
  def createBatch(id: Int, createBatchRequest: CreateBatchRequest): Batch
}

class BatchProcessFactory extends BatchFactory {
  def createBatch(id: Int, createBatchRequest: CreateBatchRequest): Batch =
    BatchProcess(id, "local[*]", createBatchRequest)
}

class BatchYarnFactory extends BatchFactory {
  def createBatch(id: Int, createBatchRequest: CreateBatchRequest): Batch =
    BatchProcess(id, "yarn-client", createBatchRequest)
}

sealed trait State

case class Running() extends State {
  override def toString = "running"
}

case class Dead() extends State {
  override def toString = "dead"
}

abstract class Batch {
  def id: Int

  def state: State

  def lines: IndexedSeq[String]

  def stop(): Future[Unit]
}

object BatchProcess {
  def apply(id: Int, master: String, createBatchRequest: CreateBatchRequest): Batch = {
    val builder = sparkBuilder(createBatchRequest)

    builder.master(master)

    val process = builder.start(createBatchRequest.file, createBatchRequest.args)
    new BatchProcess(id, new LineBufferedProcess(process))
  }

  private def sparkBuilder(createBatchRequest: CreateBatchRequest): SparkSubmitProcessBuilder = {
    val builder = SparkSubmitProcessBuilder()

    createBatchRequest.className.foreach(builder.className)
    createBatchRequest.jars.foreach(builder.jar)
    createBatchRequest.pyFiles.foreach(builder.pyFile)
    createBatchRequest.files.foreach(builder.file)
    createBatchRequest.driverMemory.foreach(builder.driverMemory)
    createBatchRequest.driverCores.foreach(builder.driverCores)
    createBatchRequest.executorMemory.foreach(builder.executorMemory)
    createBatchRequest.executorCores.foreach(builder.executorCores)
    createBatchRequest.archives.foreach(builder.archive)

    builder.redirectOutput(Redirect.PIPE)

    builder
  }
}

private class BatchProcess(val id: Int,
                           process: LineBufferedProcess) extends Batch {
  protected implicit def executor: ExecutionContextExecutor = ExecutionContext.global

  private[this] var isAlive = true

  override def state: State = {
    if (isAlive) {
      try {
        process.exitValue()
      } catch {
        case e: IllegalThreadStateException => return Running()
      }

      destroyProcess()
    }

    Dead()
  }

  override def lines: IndexedSeq[String] = process.stdoutLines

  override def stop(): Future[Unit] = {
    Future {
      destroyProcess()
    }
  }

  private def destroyProcess() = {
    process.destroy()
    process.waitFor()
    isAlive = false
  }
}
