package com.cloudera.hue.livy.repl.python

import com.cloudera.hue.livy.repl.WebApp
import org.scalatest.FunSuite
import org.scalatra.test.scalatest._

class PythonSessionSpec extends ScalatraSuite with FunSuite {

  addServlet(new WebApp(PythonSession.createPython()), "/*")

  test("it works") {
    get("/") {
      status should equal (200)
    }
  }

}
