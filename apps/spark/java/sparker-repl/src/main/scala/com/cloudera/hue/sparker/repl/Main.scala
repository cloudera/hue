package com.cloudera.hue.sparker.repl

import java.io.StringWriter

object Main {
  def main(args: Array[String]): Unit = {
    org.apache.spark.repl.Main.interp = new SparkerILoop(Console.in, new StringWriter)
    org.apache.spark.repl.Main.interp.process(args)
  }
}