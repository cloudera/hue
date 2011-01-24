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

import java.io.IOException;
import java.io.OutputStream;

/**
 * A helper class that tees an OutputStream.
 * Note that if the first OutputStream throws an exception,
 * it won't continue writing to the second one.
 */
class TeeOutputStream extends OutputStream {
  private OutputStream out1;
  private OutputStream out2;

  public TeeOutputStream(OutputStream out1, OutputStream out2) {
    super();
    this.out1 = out1;
    this.out2 = out2;
  }

  @Override
  public void write(byte[] b) throws IOException {
    if (out1 != null)
      this.out1.write(b);
    if (out2 != null)
      this.out2.write(b);
  }

  @Override
  public void write(byte[] b, int off, int len) throws IOException {
    if (out1 != null)
      this.out1.write(b, off, len);
    if (out2 != null)
      this.out2.write(b, off, len);
  }

  @Override
  public void write(int b) throws IOException {
    if (out1 != null)
      this.out1.write(b);
    if (out2 != null)
      this.out2.write(b);
  }
}