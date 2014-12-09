package com.cloudera.hue.sparker.repl

import org.scalatra.ScalatraFilter

class HelloWorldApp extends ScalatraFilter {
  get("/") {
    <h1>Hello {params("name")}</h1>
  }
}
