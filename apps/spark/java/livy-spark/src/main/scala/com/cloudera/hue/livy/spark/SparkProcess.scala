package com.cloudera.hue.livy.spark

import com.cloudera.hue.livy.LineBufferedProcess

object SparkProcess {
  def apply(process: Process): SparkProcess = {
    new SparkProcess(process)
  }
}

class SparkProcess(process: Process) extends LineBufferedProcess(process) {
}
