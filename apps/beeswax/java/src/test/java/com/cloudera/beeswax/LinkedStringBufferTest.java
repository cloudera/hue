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

import org.junit.Test;

import static org.junit.Assert.assertEquals;

public class LinkedStringBufferTest {

  @Test
  public void testBuffer() {
    LinkedStringBuffer buf = new LinkedStringBuffer(8);

    // Normal write
    buf.write("foo");
    buf.write("bar");
    assertEquals(6, buf.size());
    assertEquals("foobar", buf.read());

    // Eviction
    buf.write("baz");
    assertEquals(6, buf.size());
    assertEquals("barbaz", buf.read());

    buf.clear();
    assertEquals(0, buf.size());
    assertEquals("", buf.read());

    // Just barely fit
    String str8 = "12345678";
    buf.write(str8);
    assertEquals(8, buf.size());
    assertEquals(str8, buf.read());

    // Don't fit
    String str9 = str8 + '9';
    buf.write(str9);
    assertEquals(0, buf.size());
    assertEquals("", buf.read());
  }
}
