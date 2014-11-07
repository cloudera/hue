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

package com.cloudera.hue.sparker.server;

import com.google.common.collect.Lists;
import org.codehaus.jackson.JsonNode;
import org.codehaus.jackson.map.ObjectMapper;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.List;
import java.util.Queue;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.TimeoutException;
import java.util.logging.Level;
import java.util.logging.Logger;

public class SparkerSession implements Session {

    private static final Logger logger = Logger.getLogger("SparkerSession");

    private final String key;
    private final Process process;
    private final Thread stdoutThread;
    private final Thread stderrThread;

    private final Queue<String> inputLines = new ConcurrentLinkedQueue<String>();
    private final Queue<String> outputLines = new ConcurrentLinkedQueue<String>();

    public SparkerSession(final String key) throws IOException, InterruptedException {
        logger.info("[" + key + "]: creating sparker session");

        this.touchLastActivity();

        this.key = key;

        String sparker_home = System.getenv("SPARKER_HOME");

        ProcessBuilder pb = new ProcessBuilder(Lists.newArrayList(sparker_home + "/sparker-shell"))
                .redirectInput(ProcessBuilder.Redirect.PIPE)
                .redirectOutput(ProcessBuilder.Redirect.PIPE);

        this.process = pb.start();

        this.stdoutThread = new Thread(new Runnable() {
            @Override
            public void run() {
                BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));

                try {
                    String line;

                    ObjectMapper mapper = new ObjectMapper();

                    while ((line = reader.readLine()) != null) {
                        logger.info("[" + key + "] stdout: " + line);

                        JsonNode node = mapper.readTree(line);
                        String type = node.get("type").asText();
                        if (type.equals("ready")) {
                            outputLines.add("> ");
                        } else if (type.equals("done")) {
                            break;
                        } else  if (type.equals("result")) {
                            String output = node.get("output").asText();
                            outputLines.add(output);
                            outputLines.add("> ");
                        }
                    }

                    process.waitFor();
                } catch (IOException e) {
                    e.printStackTrace();
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
        });

        stdoutThread.start();

        this.stderrThread = new Thread(new Runnable() {
            @Override
            public void run() {
                BufferedReader reader = new BufferedReader(new InputStreamReader(process.getErrorStream()));

                try {
                    String line;

                    while ((line = reader.readLine()) != null) {
                        logger.info("[" + key + "] stderr: " + line);
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

        stderrThread.start();
    }

    @Override
    public String getKey() {
        return key;
    }

    public void execute(String command) throws IOException {
        logger.info("[" + key + "]: execute: " + command);

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
        logger.info("[" + key + "]: closing shell");
        process.getOutputStream().close();

        stdoutThread.join(1000);
        stderrThread.join(1000);

        if (stdoutThread.isAlive() || stderrThread.isAlive()) {
            stdoutThread.interrupt();
            stderrThread.interrupt();
            process.destroy();
            throw new TimeoutException();
        }

        logger.info("[" + key + "]: shell closed");
    }

    protected long lastActivity = Long.MAX_VALUE;

    public void touchLastActivity() {
        this.lastActivity = System.currentTimeMillis();
    }

    public long getLastActivity() {
        return this.lastActivity;
    }
}
