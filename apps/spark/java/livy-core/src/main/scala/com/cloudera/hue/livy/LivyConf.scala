/*
 * Licensed to Cloudera, Inc. under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  Cloudera, Inc. licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package com.cloudera.hue.livy

import java.util.concurrent.ConcurrentHashMap

import scala.collection.JavaConverters._

object LivyConf {
  val SESSION_FACTORY_KEY = "livy.server.session.factory"
  val SPARK_SUBMIT_KEY = "livy.server.spark-submit"
  val IMPERSONATION_ENABLED_KEY = "livy.impersonation.enabled"

  sealed trait SessionKind
  case class Process() extends SessionKind
  case class Yarn() extends SessionKind
}

/**
 *
 * @param loadDefaults whether to also load values from the Java system properties
 */
class LivyConf(loadDefaults: Boolean) {

  import LivyConf._

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

  /** Get a parameter as a Boolean */
  def getBoolean(key: String, default: Boolean) = getOption(key).map(_.toBoolean).getOrElse(default)

  /** Get a parameter as an Int */
  def getInt(key: String, default: Int) = getOption(key).map(_.toInt).getOrElse(default)

  /** Return if the configuration includes this setting */
  def contains(key: String): Boolean = settings.containsKey(key)

  def sparkSubmit(): String = getOption(SPARK_SUBMIT_KEY).getOrElse("spark-submit")

  def sessionKind(): SessionKind = getOption(SESSION_FACTORY_KEY).getOrElse("process") match {
    case "process" => Process()
    case "yarn" => Yarn()
    case kind => throw new IllegalStateException(f"unknown kind $kind")
  }

  /** Return the filesystem root. Defaults to the local filesystem. */
  def filesystemRoot(): String = sessionKind() match {
    case Process() => "file://"
    case Yarn() => "hdfs://"
  }
}
