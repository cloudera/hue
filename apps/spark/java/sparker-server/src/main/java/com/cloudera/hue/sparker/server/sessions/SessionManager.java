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

import java.io.IOException;
import java.util.Enumeration;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.TimeoutException;

public class SessionManager {

    public static final int UNKNOWN = 0;
    public static final int SCALA = 1;
    public static final int PYTHON = 2;

    private ConcurrentHashMap<String, Session> sessions = new ConcurrentHashMap<String, Session>();

    public SessionManager() {
        SessionManagerGarbageCollector gc = new SessionManagerGarbageCollector(this);
        gc.setDaemon(true);
        gc.start();
    }

    public Session get(String id) throws SessionNotFound {
        Session session = sessions.get(id);
        if (session == null) {
            throw new SessionNotFound(id);
        }
        return session;
    }

    public Session create(int language) throws IllegalArgumentException, IOException, InterruptedException {
        String id = UUID.randomUUID().toString();
        Session session;
        switch (language) {
            case SCALA:  session = new SparkSession(id); break;
            //case PYTHON: session = new PySparkSession(id); break;
            default: throw new IllegalArgumentException("Invalid language specified for shell session");
        }
        sessions.put(id, session);
        return session;
    }

    public void close() throws InterruptedException, IOException, TimeoutException {
        for (Session session : sessions.values()) {
            sessions.remove(session.getId());
            session.close();
        }
    }

    public void close(String id) throws InterruptedException, TimeoutException, IOException, SessionNotFound {
        Session session = this.get(id);
        sessions.remove(id);
        session.close();
    }

    public Enumeration<String> getSessionIds() {
        return sessions.keys();
    }

    public void garbageCollect() throws InterruptedException, IOException, TimeoutException {
        long timeout = 60000; // Time in milliseconds; TODO: make configurable
        for (Session session : sessions.values()) {
            long now = System.currentTimeMillis();
            if ((now - session.getLastActivity()) > timeout) {
                try {
                    this.close(session.getId());
                } catch (SessionNotFound sessionNotFound) {
                    // Ignore
                }
            }
        }
    }

    protected class SessionManagerGarbageCollector extends Thread {

        protected SessionManager manager;

        protected long period = 600000; // Time in milliseconds; TODO: make configurable

        public SessionManagerGarbageCollector(SessionManager manager) {
            super();
            this.manager = manager;
        }

        public void run() {
            try {
                while(true) {
                    manager.garbageCollect();
                    sleep(period);
                }
            } catch (InterruptedException e) {
                e.printStackTrace();
            } catch (TimeoutException e) {
                e.printStackTrace();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }

    public class SessionNotFound extends Throwable {
        public SessionNotFound(String id) {
            super(id);
        }
    }
}
