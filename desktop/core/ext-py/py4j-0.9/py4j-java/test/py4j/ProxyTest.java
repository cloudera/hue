/*******************************************************************************
 *
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
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

import java.util.ArrayList;
import java.util.List;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;

public class ProxyTest {

	private GatewayServer gServer;
	private PythonClient pClient;
	private InterfaceEntry entry;

	@Before
	public void setup() {
		// GatewayServer.turnLoggingOn();
		entry = new InterfaceEntry();
		gServer = new GatewayServer(entry);
		pClient = new PythonClient();
		gServer.start();
		pClient.startProxy();
		try {
			Thread.sleep(250);
		} catch (Exception e) {
			e.printStackTrace();
		}
	}

	@After
	public void teardown() {
		gServer.shutdown();
		pClient.stopProxy();
		try {
			Thread.sleep(300);
		} catch (Exception e) {
			e.printStackTrace();
		}
		// GatewayServer.turnLoggingOff();
	}

	@Test
	public void testSayHello() {
		String message = "c\nt\nsayHello\nfp123;py4j.IHello\ne\n";
		pClient.nextProxyReturnMessage = "ysHello\\nWorld";
		pClient.sendMesage(message);
		assertEquals("c\np123\nhello\ne\n", pClient.lastProxyMessage);
		assertEquals("ysHello\\nWorld", pClient.lastReturnMessage);
		assertEquals("Hello\nWorld", entry.simpleHello);
	}

	@Test
	public void testSayHelloWithParams() {
		String message = "c\nt\nsayHelloParams\nfp123;py4j.IHello\ne\n";
		pClient.nextProxyReturnMessage = "ysHello\\nWorld";
		pClient.sendMesage(message);
		assertEquals("c\np123\nhello2\nsTesting\\nWild\ni3\nlo0\ne\n",
				pClient.lastProxyMessage);
		assertEquals("ysHello\\nWorld", pClient.lastReturnMessage);
		assertEquals("Hello\nWorld", entry.simpleHello2);
	}

	@Test
	public void testSayHelloError() {
		assertFalse(entry.exception);
		String message = "c\nt\nsayHelloError\nfp123;py4j.IHello\ne\n";
		pClient.nextProxyReturnMessage = "x";
		pClient.sendMesage(message);
		assertEquals("c\np123\nhello\ne\n", pClient.lastProxyMessage);
		assertTrue(entry.exception);
		assertEquals("yv", pClient.lastReturnMessage);

	}

}

interface IHello {

	public String hello();

	@SuppressWarnings("rawtypes")
	public String hello2(String param1, int param2, List param3);

}

class InterfaceEntry {

	public String simpleHello;
	public String simpleHello2;
	public boolean exception = false;

	public String sayHello(IHello obj) {
		simpleHello = obj.hello();
		return simpleHello;
	}

	public String sayHelloParams(IHello obj) {
		simpleHello2 = obj.hello2("Testing\nWild", 3, new ArrayList<String>());
		return simpleHello2;
	}

	public void sayHelloError(IHello obj) {
		try {
			obj.hello();
		} catch (Py4JException e) {
			exception = true;
		}
	}

}
