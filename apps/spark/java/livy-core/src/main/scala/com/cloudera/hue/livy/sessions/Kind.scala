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

package com.cloudera.hue.livy.sessions

import org.json4s.CustomSerializer
import org.json4s.JsonAST.JString

sealed trait Kind
case class Spark() extends Kind {
  override def toString = "spark"
}

case class PySpark() extends Kind {
  override def toString = "pyspark"
}

case object SessionKindSerializer extends CustomSerializer[Kind](implicit formats => ( {
  case JString("spark") | JString("scala") => Spark()
  case JString("pyspark") | JString("python") => PySpark()
}, {
  case kind: Kind => JString(kind.toString)
}
  )
)
