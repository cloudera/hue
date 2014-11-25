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

package com.cloudera.hue.sparker.server.sessions;

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

    private static final Logger LOG = LoggerFactory.getLogger(SparkSession.class);

    private static final String SPARKER_HOME = System.getenv("SPARKER_HOME");
    private static final String SPARKER_SHELL = SPARKER_HOME + "/sparker-shell";

    private final String id;
    private final Process process;
    private final Writer writer;
    private final BufferedReader reader;
    private final List<Cell> cells = new ArrayList<Cell>();
    private final ObjectMapper objectMapper = new ObjectMapper();

    private boolean isClosed = false;

    protected long lastActivity = Long.MAX_VALUE;

    public SparkSession(final String id) throws IOException, InterruptedException {
        LOG.info("[" + id + "]: creating spark session");

        touchLastActivity();

        this.id = id;

        ProcessBuilder pb = new ProcessBuilder(Lists.newArrayList(SPARKER_SHELL))
                .redirectInput(ProcessBuilder.Redirect.PIPE)
                .redirectOutput(ProcessBuilder.Redirect.PIPE);

        this.process = pb.start();

        writer = new BufferedWriter(new OutputStreamWriter(process.getOutputStream()));
        reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
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
    synchronized public List<Cell> getCells() {
        return Lists.newArrayList(cells);
    }

    @Override
    synchronized public List<Cell> getCellRange(int fromIndex, int toIndex) {
        return cells.subList(fromIndex, toIndex);
    }

    @Override
    synchronized public Cell getCell(int index) {
        return cells.get(index);
    }

    @Override
    synchronized public Cell executeStatement(String statement) throws IOException, ClosedSessionException, InterruptedException {
        if (isClosed) {
            throw new ClosedSessionException();
        }

        touchLastActivity();

        Cell cell = new Cell(cells.size());
        cells.add(cell);

        cell.addInput(statement);

        ObjectNode request = objectMapper.createObjectNode();
        request.put("type", "stdin");
        request.put("statement", statement);

        writer.write(request.toString());
        writer.write("\n");
        writer.flush();

        String line = reader.readLine();

        if (line == null) {
            // The process must have shutdown on us!
            process.waitFor();
            throw new ClosedSessionException();
        }

        LOG.info("[" + id + "] spark stdout: " + line);

        JsonNode response = objectMapper.readTree(line);

        if (response.has("stdout")) {
            cell.addOutput(response.get("stdout").asText());
        }

        if (response.has("stderr")) {
            cell.addOutput(response.get("stderr").asText());
        }

        return cell;
    }

    @Override
    synchronized public void close() {
        isClosed = true;
        process.destroy();
    }

    private void touchLastActivity() {
        this.lastActivity = System.currentTimeMillis();
    }
}
