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
import static org.junit.Assert.assertTrue;

import java.util.List;
import java.util.concurrent.CopyOnWriteArrayList;

import org.junit.Test;

public class GatewayServerTest {

	@Test
	public void testDoubleListen() {
		GatewayServer server1 = new GatewayServer(null);
		GatewayServer server2 = new GatewayServer(null);
		boolean valid = false;

		try {
			server1.start();
			server2.start();
			valid = false;
		} catch (Py4JNetworkException network) {
			valid = true;
		} catch (Exception e) {
			valid = false;
		}

		server1.shutdown();
		server2.shutdown();

		assertTrue(valid);
	}

	@Test
	public void testListener() {
		TestListener listener = new TestListener();
		GatewayServer server1 = new GatewayServer(null);
		server1.addListener(listener);
		server1.start();
		try {
			Thread.sleep(250);
		} catch (Exception e) {

		}
		server1.shutdown();
		try {
			Thread.sleep(250);
		} catch (Exception e) {

		}
		// Started, PreShutdown, Error, Stopped, PostShutdown
		// But order cannot be guaranteed because two threads are competing.
		assertTrue(listener.values.contains(new Long(1)));
		assertTrue(listener.values.contains(new Long(10)));
		assertTrue(listener.values.contains(new Long(100)));
		assertTrue(listener.values.contains(new Long(1000)));
		assertTrue(listener.values.contains(new Long(10000)));
		assertEquals(5, listener.values.size());
	}

	@Test
	public void testEphemeralPort() {
		GatewayServer server = new GatewayServer(null, 0);
		server.start(true);
		try {
			Thread.sleep(250);
		} catch (Exception e) {

		}
		int listeningPort = server.getListeningPort();
		assertTrue(listeningPort > 0);
		assertTrue(server.getPort() != listeningPort);
		server.shutdown();
	}

}

class TestListener implements GatewayServerListener {

	public List<Long> values = new CopyOnWriteArrayList<Long>();

	@Override
	public void serverStarted() {
		values.add(new Long(1));
	}

	@Override
	public void serverStopped() {
		values.add(new Long(10));
	}

	@Override
	public void serverError(Exception e) {
		values.add(new Long(100));
	}

	@Override
	public void serverPreShutdown() {
		values.add(new Long(1000));
	}

	@Override
	public void serverPostShutdown() {
		values.add(new Long(10000));
	}

	@Override
	public void connectionStarted(GatewayConnection gatewayConnection) {
		values.add(new Long(100000));
	}

	@Override
	public void connectionStopped(GatewayConnection gatewayConnection) {
		values.add(new Long(1000000));
	}

	@Override
	public void connectionError(Exception e) {
		values.add(new Long(10000000));
	}

}