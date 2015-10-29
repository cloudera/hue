package com.cloudera.hue.livy.spark

import com.cloudera.hue.livy.LivyConf

object SparkProcessBuilderFactory {
  def apply(livyConf: LivyConf): SparkProcessBuilderFactory = {
    new SparkProcessBuilderFactory(livyConf)
  }
}

class SparkProcessBuilderFactory(val livyConf: LivyConf) {
  def builder() = {
    SparkProcessBuilder(livyConf)
  }
}
