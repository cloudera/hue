package com.cloudera.hue.livy.sessions

sealed trait Kind
case class Spark() extends Kind {
  override def toString = "spark"
}

case class PySpark() extends Kind {
  override def toString = "pyspark"
}
