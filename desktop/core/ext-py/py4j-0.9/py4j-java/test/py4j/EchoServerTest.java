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

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.fail;

import java.io.BufferedWriter;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.Reader;
import java.net.Socket;

import org.junit.Test;

public class EchoServerTest {

	@Test
	public void testConnection() {
		try {
			Thread.sleep(250);
			EchoServer.main(null);
			Thread.sleep(250);
			Socket testSocket = new Socket(GatewayServer.DEFAULT_ADDRESS,
					EchoServer.TEST_PORT);
			BufferedWriter testWriter = new BufferedWriter(
					new OutputStreamWriter(testSocket.getOutputStream()));
			// EchoServer requires end of line character to delimit commands.
			// Otherwise, it sometimes gets confused and can join two commands
			// together which is bad. I (bart) don't know why this happens.
			testWriter.write("yi7\n");
			testWriter.flush();
			testWriter.write("x\n");
			testWriter.flush();
			testWriter.close();
			testSocket.close();

			char[] buffer = new char[4092];
			Socket clientSocket = new Socket(GatewayServer.DEFAULT_ADDRESS,
					EchoServer.SERVER_PORT);
			Reader clientReader = new InputStreamReader(
					clientSocket.getInputStream());
			BufferedWriter clientWriter = new BufferedWriter(
					new OutputStreamWriter(clientSocket.getOutputStream()));

			clientWriter.write("c\nt\ngetExample\ne\n");
			clientWriter.flush();
			int count = clientReader.read(buffer);
			assertEquals(new String(buffer, 0, count), "yi7\n");
			clientWriter.write("c\no0\nmethod1\ni1\nbtrue\ne\n");
			clientWriter.flush();
			count = clientReader.read(buffer);
			assertEquals(new String(buffer, 0, count), "x\n");

			clientReader.close();
			clientWriter.close();
			clientSocket.close();
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}

}
