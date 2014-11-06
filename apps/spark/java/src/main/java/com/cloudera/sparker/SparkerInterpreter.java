/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package com.cloudera.sparker;

import org.apache.spark.repl.Main;
import org.apache.spark.repl.SparkILoop;

import java.io.*;
import java.util.UUID;

public class SparkerInterpreter implements AutoCloseable {

    private final UUID uuid;
    private final PipedWriter stdin;
    private final PipedReader stdout;
    private final SparkILoop interp;
    private final Thread thread;

    public SparkerInterpreter(UUID uuid) throws IOException {
        this.uuid = uuid;
        this.stdin = new PipedWriter();
        this.stdout = new PipedReader();
        this.interp = new SparkILoop(
                new BufferedReader(new PipedReader(stdin)),
                new PrintWriter(System.out)); //new PipedWriter(stdout)));


        Main.interp_$eq(interp);

        thread = new Thread(new Runnable() {
            @Override
            public void run() {
                interp.process(new String[]{"-usejavacp"});
            }
        });
    }

    public UUID getUUID() {
        return uuid;
    }

    public void execute(String command) throws IOException {
        stdin.write(command);
        stdin.write("\n");
    }

    public void start() throws IOException {
        thread.start();
    }

    @Override
    public void close() throws Exception {
        stdin.close();
        stdout.close();
        thread.join();
    }
}
