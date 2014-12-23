package com.cloudera.hue.livy

trait Request

case class ExecuteRequest(statement: String) extends Request
case class ShutdownRequest() extends Request
