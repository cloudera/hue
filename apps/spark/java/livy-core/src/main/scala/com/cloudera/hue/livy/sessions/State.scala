package com.cloudera.hue.livy.sessions

sealed trait State

case class NotStarted() extends State {
  override def toString = "not_started"
}

case class Starting() extends State {
  override def toString = "starting"
}

case class Idle() extends State {
  override def toString = "idle"
}

case class Busy() extends State {
  override def toString = "busy"
}

case class Error() extends State {
  override def toString = "error"
}

case class ShuttingDown() extends State {
  override def toString = "shutting_down"
}

case class Dead() extends State {
  override def toString = "dead"
}
