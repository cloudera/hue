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

import org.codehaus.jackson.map.ObjectMapper;
import org.codehaus.jackson.map.ObjectWriter;

import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.BufferedReader;
import java.io.IOException;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class SparkerServlet extends HttpServlet {

    public static final String SESSION_DATA = "sparky.sessions";

    private static final String ROOT = "/";
    private static final Pattern SESSION_ID = Pattern.compile("^/([-A-Za-z90-9]+)$");

    private static final String APPLICATION_JSON_MIME = "application/json";

    private ObjectWriter jsonWriter;

    private final SessionManager manager;

    public SparkerServlet(SessionManager manager) {
        this.manager = manager;

        ObjectMapper mapper = new ObjectMapper();
        jsonWriter = mapper.defaultPrettyPrintingWriter();
    }

    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        resp.setContentType(APPLICATION_JSON_MIME);
        resp.setStatus(HttpServletResponse.SC_OK);

        String requestType = req.getPathInfo();
        requestType = (requestType != null) ? requestType.toLowerCase() : ROOT;

        if (requestType.equals(ROOT)) {
            getSessions(req, resp);
        } else {
            Matcher m = SESSION_ID.matcher(requestType);
            if (m.matches()) {
                String key = m.group(1);
                getSession(req, resp, key);
            } else {
                resp.setStatus(HttpServletResponse.SC_NOT_FOUND);
            }
        }
    }

    private void getSessions(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        jsonWriter.writeValue(resp.getOutputStream(), manager.getSessionKeys());
    }

    private void getSession(HttpServletRequest req, HttpServletResponse resp, String key) throws IOException {
        Session session = manager.get(key);
        if (session == null) {
            resp.setStatus(HttpServletResponse.SC_NOT_FOUND);
            return;
        }

        jsonWriter.writeValue(resp.getOutputStream(), session.getOutputLines());
    }

    @Override
    protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        resp.setContentType(APPLICATION_JSON_MIME);
        resp.setStatus(HttpServletResponse.SC_OK);

        String requestType = req.getPathInfo();
        requestType = (requestType != null) ? requestType.toLowerCase() : ROOT;

        if (requestType.equals(ROOT)) {
            createSession(req, resp);
        } else {
            Matcher m = SESSION_ID.matcher(requestType);
            if (m.matches()) {
                String key = m.group(1);
                writeToSession(req, resp, key);
            } else {
                resp.setStatus(HttpServletResponse.SC_NOT_FOUND);
            }
        }
    }

    @Override
    protected void doDelete(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        resp.setContentType(APPLICATION_JSON_MIME);
        resp.setStatus(HttpServletResponse.SC_OK);

        String requestType = req.getPathInfo();
        requestType = (requestType != null) ? requestType.toLowerCase() : ROOT;

        if (requestType.equals(ROOT)) {
            resp.setStatus(HttpServletResponse.SC_METHOD_NOT_ALLOWED);
        } else {
            Matcher m = SESSION_ID.matcher(requestType);
            if (m.matches()) {
                String key = m.group(1);
                manager.close(key);
            } else {
                resp.setStatus(HttpServletResponse.SC_NOT_FOUND);
            }
        }
    }

    private void createSession(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        try {
            Session session = manager.create();

            jsonWriter.writeValue(resp.getOutputStream(), session.getKey());
        } catch (InterruptedException e) {
            resp.setStatus(HttpServletResponse.SC_INTERNAL_SERVER_ERROR);
            e.printStackTrace();
        }
    }

    private void writeToSession(HttpServletRequest req, HttpServletResponse resp, String key) throws IOException {
        Session session = manager.get(key);
        if (session == null) {
            resp.setStatus(HttpServletResponse.SC_NOT_FOUND);
            return;
        }

        BufferedReader reader = req.getReader();
        String line;

        while ((line = reader.readLine()) != null) {
            session.execute(line);
        }
    }

}
