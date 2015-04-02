package com.cloudera.hue.livy.server.batch

import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.atomic.AtomicInteger

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
    BatchProcess(id, createBatchRequest)
}

abstract class Batch {
  def id: Int

  def stop(): Future[Unit]
}

object BatchProcess {
  def apply(id: Int, createBatchRequest: CreateBatchRequest): Batch = {
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

    val process = builder.start(createBatchRequest.file, createBatchRequest.args)
    new BatchProcess(id, process)
  }
}

private class BatchProcess(val id: Int,
                           @transient
                           process: Process) extends Batch {
  protected implicit def executor: ExecutionContextExecutor = ExecutionContext.global

  override def stop(): Future[Unit] = {
    Future {
      process.destroy()
      process.waitFor()
    }
  }
}
