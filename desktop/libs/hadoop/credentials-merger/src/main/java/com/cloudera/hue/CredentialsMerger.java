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
package com.cloudera.hue;

import java.io.IOException;
import java.io.File;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.security.Credentials;

/**
 * A tool to merge the credentials of multiple distinct files containing Hadoop
 * delegation tokens into a single file.
 */
public class CredentialsMerger {
  
  /**
   * Merge several credentials files into one. Give the desired output file
   * first, followed by all of the input files.
   *
   * @param args &lt;out&gt; &lt;in1&gt; ...
   * @throws IOException  in the event of an error reading or writing files.
   */
  public static void main(String[] args) throws IOException {
    if (args.length < 2) {
      printUsage();
      System.exit(1);
    }

    Path outputFile = new Path("file://" + new File(args[0]).getAbsolutePath());
    Configuration conf = new Configuration();
    Credentials credentials = new Credentials();
    for (int i = 1; i < args.length; i++) {
      Credentials singleFileCredentials = Credentials.readTokenStorageFile(
          new Path("file://" + new File(args[i]).getAbsolutePath()), conf);
      credentials.addAll(singleFileCredentials);
    }

    credentials.writeTokenStorageFile(outputFile, conf);
  }
  
  /**
   * Show command usage.
   */
  private static void printUsage() {
    System.err.println("Usage: " + CredentialsMerger.class.getCanonicalName()
        + " <dst> <src> ...");
  }

}
