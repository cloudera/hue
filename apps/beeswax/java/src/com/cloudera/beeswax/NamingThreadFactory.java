// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package com.cloudera.beeswax;

import java.util.concurrent.ThreadFactory;
import java.util.concurrent.atomic.AtomicInteger;

/** Names threads */
class NamingThreadFactory implements ThreadFactory {
  private final AtomicInteger count = new AtomicInteger(0);
  private final String template;

  /** Template is expected to have a "%d" in it for an incrementing counter. */
  public NamingThreadFactory(String template) {
    this.template = template;
  }

  @Override
  public Thread newThread(Runnable r) {
    Thread t = new Thread(r);
    t.setName(String.format(template, count.getAndIncrement()));
    return t;
  }
}
