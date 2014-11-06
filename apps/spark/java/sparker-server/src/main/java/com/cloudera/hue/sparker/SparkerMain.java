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

package com.cloudera.hue.sparker;

import org.eclipse.jetty.server.Server;
import org.eclipse.jetty.servlet.ServletContextHandler;
import org.eclipse.jetty.servlet.ServletHolder;

public class SparkerMain {

    public static void main(String[] args) throws Exception {
        SessionManager manager = new SessionManager();

        Server httpServer = new Server(8080);

        ServletContextHandler context = new ServletContextHandler();
        httpServer.setHandler(context);

        context.setContextPath("/");
        context.addServlet(new ServletHolder(new SparkerServlet(manager)), "/*");

        /*
        //InetSocketAddress address = NetUtils.createSocketAddr()
        ServletContextHandler.Context context = new ServletContextHandler.Context();
        context.setContextPath("");
        context.addServlet(JMXJsonServlet.class, "/jmx");
        context.addServlet(SparkerServlet.class, "/*");

        httpServer.addHandler(context);
        */

        httpServer.start();
        httpServer.join();

        /*
        BufferedReader reader = new BufferedReader(new StringReader(""));
        StringWriter writer = new StringWriter();
        String master = "erickt-1.ent.cloudera.com";

        SparkILoop interp = new SparkILoop(reader, new PrintWriter(writer));
        Main.interp_$eq(interp);
        interp.process(new String[] { "-usejavacp" });
        */

        /*
        SparkerInterpreter session = new SparkerInterpreter(UUID.randomUUID());

        try {
            session.start();

            session.execute("sc");
            session.execute("1 + 1");

        } finally {
            session.close();
        }
        */

        /*
        SessionManager manager = new SessionManager();

        try {
            Session session = manager.create();

            session.execute("sc");
            session.execute("1 + 1");

            for (String input : session.getInputLines()) {
                System.out.print("input: " + input + "\n");
            }

            for (String output : session.getOutputLines()) {
                System.out.print("output: " + output + "\n");
            }

        } finally {
            manager.close();
        }
        */
    }
}
