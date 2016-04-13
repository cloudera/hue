/*******************************************************************************
 * Copyright (c) 2009, 2011, Barthelemy Dagenais All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * - Redistributions of source code must retain the above copyright notice, this
 * list of conditions and the following disclaimer.
 *
 * - Redistributions in binary form must reproduce the above copyright notice,
 * this list of conditions and the following disclaimer in the documentation
 * and/or other materials provided with the distribution.
 *
 * - The name of the author may not be used to endorse or promote products
 * derived from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 *******************************************************************************/
package py4j;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.net.ServerSocket;
import java.net.Socket;
import java.nio.charset.Charset;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingQueue;

public class EchoServer {

	public static final int TEST_PORT = 25332;

	public static final int SERVER_PORT = 25333;

	private int testPort = TEST_PORT;

	private int serverPort = SERVER_PORT;

	private final BlockingQueue<String> queue = new LinkedBlockingQueue<String>();

	public int getTestPort() {
		return testPort;
	}

	public void setTestPort(int testPort) {
		this.testPort = testPort;
	}

	public int getServerPort() {
		return serverPort;
	}

	public void setServerPort(int serverPort) {
		this.serverPort = serverPort;
	}

	private void setupTestServer() {
		Thread t = new Thread(new Runnable() {

			@Override
			public void run() {
				ServerSocket sSocket = null;
				Socket testSocket = null;
				try {
					sSocket = new ServerSocket(testPort);
					testSocket = sSocket.accept();
					BufferedReader reader = new BufferedReader(
							new InputStreamReader(testSocket.getInputStream(),
									Charset.forName("UTF-8")));
					while (true) {
						System.out.println("Waiting for echo input.");
						String command = reader.readLine();
						System.out.println("Echo received: " + command);
						if (command == null) {
							break;
						}
						queue.put(command);
					}
				} catch (Exception e) {
					e.printStackTrace();
				} finally {
					NetworkUtil.quietlyClose(testSocket);
					NetworkUtil.quietlyClose(sSocket);
				}
			}

		});

		t.start();
	}

	private void setupServer() {
		Thread t = new Thread(new Runnable() {

			@Override
			public void run() {
				ServerSocket sSocket = null;
				Socket clientSocket = null;
				try {
					sSocket = new ServerSocket(serverPort);
					clientSocket = sSocket.accept();
					BufferedReader reader = new BufferedReader(
							new InputStreamReader(
									clientSocket.getInputStream(),
									Charset.forName("UTF-8")));
					BufferedWriter writer = new BufferedWriter(
							new OutputStreamWriter(
									clientSocket.getOutputStream(),
									Charset.forName("UTF-8")));
					while (true) {
						String command = readCommand(reader);
						if (command == null) {
							break;
						}
						String returnCommand = queue.poll();
						System.out.println(returnCommand);
						writer.write(returnCommand + "\n");
						writer.flush();
					}
				} catch (Exception e) {
					e.printStackTrace();
				} finally {
					NetworkUtil.quietlyClose(clientSocket);
					NetworkUtil.quietlyClose(sSocket);
				}
			}

			private String readCommand(BufferedReader reader)
					throws IOException {
				System.out.println("Reading commands");
				StringBuilder commandBuilder = new StringBuilder();

				while (true) {
					String temp = reader.readLine();
					System.out.println("Received temp: " + temp);
					if (temp != null) {
						commandBuilder.append(temp);
						commandBuilder.append("\n");
						if (temp.trim().equals("e")) {
							break;
						}
					} else {
						break;
					}
				}

				String command = commandBuilder.toString().trim();
				if (command.length() == 0) {
					command = null;
				}

				return command;
			}

		});

		t.start();
	}

	public static void main(String[] args) {
		EchoServer echoServer = new EchoServer();
		echoServer.setupTestServer();
		echoServer.setupServer();
		System.out.println("EchoServer started...");
	}

}
