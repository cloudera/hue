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

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.util.Enumeration;
import java.util.UUID;
import java.util.concurrent.*;

public class SessionManager {

    private static final Logger LOG = LoggerFactory.getLogger(SparkSession.class);

    public enum SessionType {
        SCALA,
        PYTHON,
    }

    private ConcurrentHashMap<String, Session> sessions = new ConcurrentHashMap<String, Session>();
    private BlockingQueue<Session> freshScalaSessions = new LinkedBlockingQueue<Session>(5);

    SessionManagerGarbageCollector gcThread = new SessionManagerGarbageCollector();
    SessionCreator creatorThread = new SessionCreator(SessionType.SCALA);

    public SessionManager() {
        gcThread.setDaemon(true);
        gcThread.start();

        creatorThread.setDaemon(true);
        creatorThread.start();
    }

    public Session get(String id) throws SessionNotFound {
        Session session = sessions.get(id);
        if (session == null) {
            throw new SessionNotFound(id);
        }
        return session;
    }

    public Session create(SessionType type) throws IllegalArgumentException, IOException, InterruptedException {
        Session session;
        switch (type) {
            case SCALA: session = freshScalaSessions.take(); break;
            //case PYTHON: session = new PySparkSession(id); break;
            default: throw new IllegalArgumentException("Invalid language specified for shell session");
        }
        sessions.put(session.getId(), session);
        return session;
    }

    public void close() throws InterruptedException, IOException, TimeoutException {
        for (Session session : sessions.values()) {
            sessions.remove(session.getId());
            session.close();
        }

        gcThread.interrupt();
        gcThread.join();
        creatorThread.interrupt();
        creatorThread.join();

        Session session;
        while ((session = freshScalaSessions.poll(500, TimeUnit.MILLISECONDS)) != null) {
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

    private class SessionManagerGarbageCollector extends Thread {

        protected long period = 1000 * 60 * 60; // Time in milliseconds; TODO: make configurable

        public SessionManagerGarbageCollector() {
            super();
        }

        public void run() {
            try {
                while(true) {
                    garbageCollect();
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

    private class SessionCreator extends Thread {
        SessionType type;

        public SessionCreator(SessionType type) {
            this.type = type;
        }

        public void run() {
            try {
                while(true) {
                    String id = UUID.randomUUID().toString();

                    Session session;
                    switch (type) {
                        case SCALA: session = new SparkSession(id); break;
                        //case PYTHON: session = new PythonSession(id); break;
                        default: throw new IllegalArgumentException("Invalid language specified for shell session");
                    }

                    freshScalaSessions.put(session);
                }
            } catch (InterruptedException e) {
                e.printStackTrace();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }
}
