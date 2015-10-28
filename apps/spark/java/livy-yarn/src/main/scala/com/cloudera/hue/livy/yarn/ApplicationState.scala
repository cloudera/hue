package com.cloudera.hue.livy.yarn

sealed trait ApplicationState

object ApplicationState {
  case class New() extends ApplicationState
  case class Accepted() extends ApplicationState
  case class Running() extends ApplicationState
  case class SuccessfulFinish() extends ApplicationState
  case class UnsuccessfulFinish() extends ApplicationState
}