package com.cloudera.hue.livy

import org.slf4j.LoggerFactory

trait Logging {
  lazy val logger = LoggerFactory.getLogger(this.getClass)

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

  def error(message: => Any, t: Throwable) = {
    logger.error(message.toString, t)
  }

  def error(message: => Any) = {
    logger.error(message.toString)
  }
}
