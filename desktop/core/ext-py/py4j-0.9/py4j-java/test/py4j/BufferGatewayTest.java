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

import org.junit.Test;

import py4j.examples.BufferGenerator;

public class BufferGatewayTest {

	@Test
	public void testBufferedGateway1() {
		BufferGenerator.main(null);

		EchoClient client = new EchoClient();

		try {
			Thread.sleep(250);
			client.connect();

			client.write("c\nt\ngetStringBuffer\ne\n");
			assertEquals(client.getResponse(), "yro0\n");
			client.write("c\no0\nappend\nd1.1\ne\n");
			assertEquals(client.getResponse(), "yro1\n");
			client.write("c\no0\ntoString\ne\n");
			assertEquals(client.getResponse(), "ysFromJava1.1\n");
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		} finally {
			client.close();
			BufferGenerator.shutdownGateway();
		}
	}

}
