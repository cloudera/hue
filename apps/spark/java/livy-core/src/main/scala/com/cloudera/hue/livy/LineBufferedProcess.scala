package com.cloudera.hue.livy

import scala.io.Source

class LineBufferedProcess(process: Process) extends Logging {

  private[this] var _stdoutLines: IndexedSeq[String] = IndexedSeq()
  private[this] var _stderrLines: IndexedSeq[String] = IndexedSeq()

  private val stdoutThread = new Thread {
    override def run() = {
      val lines = Source.fromInputStream(process.getInputStream).getLines()
      for (line <- lines) {
        trace("stdout: ", line)
        _stdoutLines +:= line
      }
    }
  }
  stdoutThread.setDaemon(true)
  stdoutThread.start()

  private val stderrThread = new Thread {
    override def run() = {
      val lines = Source.fromInputStream(process.getErrorStream).getLines()
      for (line <- lines) {
        trace("stderr: ", line)
        _stderrLines +:= line
      }
    }
  }
  stderrThread.setDaemon(true)
  stderrThread.start()

  def stdoutLines: IndexedSeq[String] = _stdoutLines

  def stderrLines: IndexedSeq[String] = _stderrLines

  def destroy(): Unit = {
    process.destroy()
  }

  def exitValue(): Int = {
    process.exitValue()
  }

  def waitFor(): Int = {
    val output = process.waitFor()
    stdoutThread.join()
    stderrThread.join()
    output
  }
}
