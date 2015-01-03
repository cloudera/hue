package com.cloudera.hue.livy

case class ExecuteResponse(id: Int /*, state: State*/, input: List[String], output: List[String])

sealed trait State
case class Ready() extends State
case class Incomplete() extends State
case class Running() extends State
case class Complete() extends State
