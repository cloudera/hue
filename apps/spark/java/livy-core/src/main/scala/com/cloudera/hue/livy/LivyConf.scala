package com.cloudera.hue.livy

import java.util.concurrent.ConcurrentHashMap

import scala.collection.JavaConverters._

object LivyConf {

}

/**
 *
 * @param loadDefaults whether to also load values from the Java system properties
 */
class LivyConf(loadDefaults: Boolean) {
  /**
   * Create a LivyConf that loads defaults from the system properties and the classpath.
   * @return
   */
  def this() = this(true)

  private val settings = new ConcurrentHashMap[String, String]

  if (loadDefaults) {
    for ((k, v) <- System.getProperties.asScala if k.startsWith("livy.")) {
      settings.put(k, v)
    }
  }

  /** Set a configuration variable */
  def set(key: String, value: String): LivyConf = {
    if (key == null) {
      throw new NullPointerException("null key")
    }

    if (value == null) {
      throw new NullPointerException("null key")
    }

    settings.put(key, value)
    this
  }

  /** Set if a parameter is not already configured */
  def setIfMissing(key: String, value: String): LivyConf = {
    if (!settings.contains(key)) {
      settings.put(key, value)
    }
    this
  }

  /** Get a configuration variable */
  def get(key: String): String = getOption(key).getOrElse(throw new NoSuchElementException(key))

  /** Get a configuration variable */
  def get(key: String, default: String): String = getOption(key).getOrElse(default)

  /** Get a parameter as an Option */
  def getOption(key: String): Option[String] = Option(settings.get(key))

  /** Get a parameter as an Int */
  def getInt(key: String, default: Int) = getOption(key).map(_.toInt).getOrElse(default)

  /** Return if the configuration includes this setting */
  def contains(key: String): Boolean = settings.contains(key)
}
