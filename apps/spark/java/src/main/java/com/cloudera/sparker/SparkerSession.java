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

import com.google.common.collect.Lists;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.List;
import java.util.Queue;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeoutException;

public class SparkerSession implements Session {

    private final String key;
    private final Process process;
    private final Thread readerThread;

    private final Queue<String> inputLines = new ConcurrentLinkedQueue<String>();
    private final Queue<String> outputLines = new ConcurrentLinkedQueue<String>();

    public SparkerSession(String key) throws IOException, InterruptedException {
        this.touchLastActivity();

        this.key = key;

        ProcessBuilder pb = new ProcessBuilder("spark-shell")
                .redirectInput(ProcessBuilder.Redirect.PIPE)
                .redirectOutput(ProcessBuilder.Redirect.PIPE)
                .redirectErrorStream(true);

        this.process = pb.start();

        final CountDownLatch latch = new CountDownLatch(1);

        this.readerThread = new Thread(new Runnable() {
            @Override
            public void run() {
                BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));

                try {
                    String line;

                    /*
                    while ((line = reader.readLine()) != null) {
                        outputLines.add(line);
                        if (line.equals("Spark context available as sc.")) {
                            latch.countDown();
                        }
                    }
                    */

                    while ((line = reader.readLine()) != null) {
                        outputLines.add(line);
                    }

                    process.waitFor();
                } catch (IOException e) {
                    e.printStackTrace();
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
        });

        readerThread.start();

        //latch.await();
    }

    @Override
    public String getKey() {
        return key;
    }

    public void execute(String command) throws IOException {
        this.touchLastActivity();
        if (!command.endsWith("\n")) {
            command += "\n";
        }

        inputLines.add(command);
        process.getOutputStream().write(command.getBytes("UTF-8"));
        process.getOutputStream().flush();
    }

    @Override
    public List<String> getInputLines() {
        this.touchLastActivity();
        return Lists.newArrayList(inputLines);
    }

    @Override
    public List<String> getOutputLines() {
        this.touchLastActivity();
        return Lists.newArrayList(outputLines);
    }

    public void close() throws IOException, InterruptedException, TimeoutException {
        process.getOutputStream().close();

        readerThread.join();
        if (readerThread.isAlive()) {
            readerThread.interrupt();
            process.destroy();
            throw new TimeoutException();
        }
    }

    protected long lastActivity = Long.MAX_VALUE;

    public void touchLastActivity() {
        long now = System.currentTimeMillis();
        this.lastActivity = now;
    }

    public long getLastActivity() {
        return this.lastActivity;
    }
}
