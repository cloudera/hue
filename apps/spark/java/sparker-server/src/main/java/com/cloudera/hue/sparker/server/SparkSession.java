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

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.Lists;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.*;
import java.util.ArrayList;
import java.util.List;

/**
 * The SparkSession works by spawning off a worker process and communicating with it over a simple IPC json protocol.
 *
 * The request is a json dictionary with the following fields:
 *
 * - id: the cell id.
 * - type: the kind of command.
 * - stdin: the command to execute.
 *
 * The response is a json dictionary with the following fields:
 *
 * - id: the cell this message corresponds to.
 * - state: what state the interpreter is in. One of [ready, incomplete, running, complete]
 * - stdout: the STDOUT lines.
 * - stderr: the STDERR lines.
 *
 * The way it works is that we spawn a worker thread th
 */
public class SparkSession implements Session {

    private static final String SPARKER_HOME = System.getenv("SPARKER_HOME");
    private static final String SPARKER_SHELL = SPARKER_HOME + "/sparker-shell";

    private static final Logger logger = LoggerFactory.getLogger(SparkSession.class);

    private final String id;
    private final Process process;
    private final Writer writer;
    private final BufferedReader reader;
    private final List<Cell> cells = new ArrayList<Cell>();
    private final ObjectMapper objectMapper = new ObjectMapper();
    private final Thread thread;
    private boolean isClosed = false;

    protected long lastActivity = Long.MAX_VALUE;

    public SparkSession(final String id) throws IOException, InterruptedException {
        logger.info("[" + id + "]: creating spark session");

        touchLastActivity();

        this.id = id;

        cells.add(new Cell());

        ProcessBuilder pb = new ProcessBuilder(Lists.newArrayList(SPARKER_SHELL))
                .redirectInput(ProcessBuilder.Redirect.PIPE)
                .redirectOutput(ProcessBuilder.Redirect.PIPE);

        this.process = pb.start();

        this.writer = new BufferedWriter(new OutputStreamWriter(process.getOutputStream()));
        this.reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
    }

    @Override
    public String getId() {
        return id;
    }


    @Override
    public long getLastActivity() {
        return this.lastActivity;
    }

    @Override
    public List<Cell> getCells() {
        return cells;
    }

    @Override
    public Cell executeStatement(String statement) throws IOException, ClosedSessionException {
        if (isClosed) {
            throw new ClosedSessionException();
        }

        touchLastActivity();

        Cell cell = cells.get(cells.size() - 1);
        cell.addInput(statement);

        ObjectNode request = objectMapper.createObjectNode();
        request.put("type", "execute-statement");
        request.put("statement", statement);

        writer.write(request.toString());

        String line;

        while ((line = reader.readLine()) != null) {
            JsonNode response = objectMapper.readTree(line);

            if (response.has("stdout")) {
                cell.addOutput(response.get("stdout").asText());
            }

            if (response.has("stderr")) {
                cell.addOutput(response.get("stderr").asText());
            }

            String state = response.get("state").asText();

            if (state.equals("complete") || state.equals("incomplete")) {
                break;
            }
        }

        return cell;
    }

    public void

    @Override
    public void close() {
        isClosed = true;

        if (process.isAlive()) {
            process.destroy();
        }
    }

    private void touchLastActivity() {
        this.lastActivity = System.currentTimeMillis();
    }


    /*

        this.stdoutThread = new Thread(new Runnable() {
            @Override
            public void run() {
                BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));

                try {
                    String line;

                    ObjectMapper mapper = new ObjectMapper();

                    while ((line = reader.readLine()) != null) {
                        logger.info("[" + id + "] spark stdout: " + line);

                        JsonNode node = mapper.readTree(line);

                        String state = node.get("state").asText();

                        lock.lock();
                        try {
                            Cell cell = cells.get(cells.size() - 1);

                            if (state.equals("ready")) {
                                cell.setState(Cell.State.READY);
                            } else  if (state.equals("incomplete")) {
                                cell.setState(Cell.State.INCOMPLETE);
                            } else if (state.equals("running")) {
                                cell.setState(Cell.State.RUNNING);
                            } else if (state.equals("complete")) {
                                cell.setState(Cell.State.COMPLETE);

                                // Start a new cell.
                                cells.add(new Cell());
                            }

                            if (node.has("stdout")) {
                                cell.addOutput(node.get("stdout").asText());
                            }

                            if (node.has("stderr")) {
                                cell.addOutput(node.get("stderr").asText());
                            }

                        } finally {
                            lock.unlock();
                        }
                    }

                    int exitCode = process.waitFor();
                    logger.info("[" + id + "]: process exited with " + exitCode);
                } catch (IOException e) {
                    e.printStackTrace();
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
        });

        stdoutThread.start();

        /*
        this.stderrThread = new Thread(new Runnable() {
            @Override
            public void run() {
                BufferedReader reader = new BufferedReader(new InputStreamReader(process.getErrorStream()));

                try {
                    String line;

                    ObjectMapper mapper = new ObjectMapper();

                    while ((line = reader.readLine()) != null) {
                        logger.info("[" + id + "] stderr: " + line);



                        ObjectNode node = mapper.createObjectNode();
                        node.put("type", "stderr");
                        node.put("msg", line);

                        outputLines.add(node);
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
        * /
    }

    @Override
    public String getKey() {
        return id;
    }

    public void execute(String command) throws IOException {
        logger.info("[" + id + "]: execute: " + command);

        this.touchLastActivity();
        if (!command.endsWith("\n")) {
            command += "\n";
        }

        inputLines.add(command);
        process.getOutputStream().write(command.getBytes("UTF-8"));
        process.getOutputStream().flush();
    }

    /*
    @Override
    public List<String> getInputLines() {
        this.touchLastActivity();
        return Lists.newArrayList(inputLines);
    }
    * /

    /*
    @Override
    public List<JsonNode> getOutputLines() {
        this.touchLastActivity();
        return Lists.newArrayList(outputLines);
    }
    * /

    public List<Cell> getCells() {
        lock.lock();
        try {
            return Lists.newArrayList(cells);
        } finally {
            lock.unlock();
        }
    }

    public void close() throws IOException, InterruptedException, TimeoutException {
        logger.info("[" + id + "]: closing shell");
        process.getOutputStream().close();

        stdoutThread.join(1000);
        //stderrThread.join(1000);

        if (stdoutThread.isAlive()) { // || stderrThread.isAlive()) {
            stdoutThread.interrupt();
            //stderrThread.interrupt();
            process.destroy();
            throw new TimeoutException();
        }

        logger.info("[" + id + "]: shell closed with " + process.exitValue());
    }

    */
}
