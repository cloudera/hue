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

import java.util.LinkedList;

/**
 * A linked string buffer with a capacity limit.
 */
public class LinkedStringBuffer {

  private final LinkedList<String> list;
  private final int capacity;
  private int size;

  /**
   * Create a buffer with the specified capacity on the number of characters.
   */
  public LinkedStringBuffer(int capacity) {
    this.capacity = capacity;
    list = new LinkedList<String>();
  }

  /**
   * @return Size (number of characters) in the buffer
   */
  public synchronized int size() {
    return size;
  }

  /**
   * Write to the buffer, which will remove previously written strings if
   * we don't fit in capacity.
   */
  public synchronized void write(String data) {
    list.add(data);
    size += data.length();

    // Trim from the front
    while (size > capacity) {
      String evicted = list.remove(0);
      size -= evicted.length();
    }
  }

  /**
   * @return All the data in the buffer.
   */
  public synchronized String read() {
    StringBuilder sb = new StringBuilder();
    for (String s : list) {
      sb.append(s);
    }
    return sb.toString();
  }

  /**
   * Remove all stored data.
   */
  public synchronized void clear() {
    list.clear();
    size = 0;
  }
}
