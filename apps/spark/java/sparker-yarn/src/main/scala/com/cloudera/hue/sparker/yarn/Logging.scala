package com.cloudera.hue.sparker.yarn

import org.slf4j.LoggerFactory

trait Logging {
  val loggerName = this.getClass.getName
  lazy val logger = LoggerFactory.getLogger(loggerName)

  def debug(message: => Any) = {
    if (logger.isDebugEnabled) {
      logger.debug(message.toString)
    }
  }

  def info(message: => Any) = {
    if (logger.isInfoEnabled) {
      logger.info(message.toString)
    }
  }

  def warn(message: => Any) = {
    logger.warn(message.toString)
  }

  def error(message: => Any) = {
    logger.error(message.toString)
  }
}
