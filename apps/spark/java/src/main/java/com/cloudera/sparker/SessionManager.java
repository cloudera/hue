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

import java.io.IOException;
import java.util.Enumeration;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.TimeoutException;

public class SessionManager {

    private ConcurrentHashMap<String, SparkerSession> sessions = new ConcurrentHashMap<String, SparkerSession>();

    public SessionManager() {

    }

    public Session get(String key) {
        return sessions.get(key);
    }

    public Session create() throws IOException, InterruptedException {
        String key = UUID.randomUUID().toString();
        SparkerSession session = new SparkerSession(key);
        sessions.put(key, session);
        return session;
    }

    public void close() throws InterruptedException, TimeoutException, IOException {
        for (SparkerSession session : sessions.values()) {
            session.close();
        }
    }

    public Enumeration<String> getSessionKeys() {
        return sessions.keys();
    }
}
