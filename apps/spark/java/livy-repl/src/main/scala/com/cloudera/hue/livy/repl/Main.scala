package com.cloudera.hue.livy.repl

object Main {
  def main(args: Array[String]): Unit = {
    val port = sys.env.getOrElse("PORT", "8999").toInt
    val server = new WebServer(port)
    server.start()
    server.join()

    server.start()
    server.join()
    server.stop()
  }
}
