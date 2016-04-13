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
package py4j.commands;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;
import static org.junit.Assert.fail;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.StringReader;
import java.io.StringWriter;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;

import py4j.Gateway;
import py4j.examples.ExampleClass;
import py4j.examples.ExampleEntryPoint;

public class CallCommandTest {

	private ExampleEntryPoint entryPoint;
	private Gateway gateway;
	private CallCommand command;
	private BufferedWriter writer;
	private StringWriter sWriter;
	private String target;

	@Before
	public void setUp() {
		entryPoint = new ExampleEntryPoint();
		gateway = new Gateway(entryPoint);
		gateway.startup();
		command = new CallCommand();
		command.init(gateway);
		sWriter = new StringWriter();
		writer = new BufferedWriter(sWriter);
		target = gateway.putNewObject(entryPoint.getNewExample());
	}

	@After
	public void tearDown() {
		gateway.shutdown();
	}

	@Test
	public void testStatic() {
		String inputCommand = "z:java.lang.String\nvalueOf\ni123\ne\n";
		try {
			command.execute("c", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertEquals("ys123\n", sWriter.toString());
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}

	@Test
	public void testReflectionException() {
		String inputCommand = "z:java.lang.String\nvalueOf2\ni123\ne\n";
		try {
			command.execute("c", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertTrue(sWriter.toString().startsWith("xspy4j.Py4JException: "));
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}

	@Test
	public void testReflectionException2() {
		String inputCommand = target + "\nmethod1aa\ne\n";
		try {
			command.execute("c", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertTrue(sWriter.toString().startsWith("xspy4j.Py4JException: "));
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}

	@Test
	public void testClientCodeException() {
		String inputCommand = "z:java.lang.Integer\nvalueOf\nsallo\ne\n";
		try {
			command.execute("c", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertEquals("xro1\n", sWriter.toString());
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}

	@Test
	public void testNoParam() {
		String inputCommand = target + "\nmethod1\ne\n";
		try {
			command.execute("c", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertEquals("yi1\n", sWriter.toString());
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}

	@Test
	public void testVoidMethod() {
		String inputCommand = target + "\nmethod2\nsThis is a\tString\\n\ne\n";
		try {
			command.execute("c", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertEquals("yv\n", sWriter.toString());
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}

	@Test
	public void testMethodWithNull() {
		String inputCommand = target + "\nmethod2\nn\ne\n";
		try {
			command.execute("c", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertEquals("yv\n", sWriter.toString());

			inputCommand = target + "\nmethod4\nn\ne\n";
			command.execute("c", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertEquals("yv\nyro1\n", sWriter.toString());
			assertEquals(((ExampleClass) gateway.getObject("o1")).getField1(),
					3);

			inputCommand = target + "\nmethod7\nn\ne\n";
			command.execute("c", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertEquals("yv\nyro1\nyi2\n", sWriter.toString());
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}

	@Test
	public void testMethodWithParams() {
		String inputCommand = target + "\nmethod3\ni1\nbtrue\ne\n";
		try {
			command.execute("c", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertEquals("ysHello World\n", sWriter.toString());
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}

	@Test
	public void testCharMethod() {
		String inputCommand = target + "\nmethod4\nsc\ne\n";
		try {
			command.execute("c", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertEquals("yro1\n", sWriter.toString());
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}

	@Test
	public void testCharMethod2() {
		String inputCommand = target + "\nmethod6\nsc\ne\n";
		try {
			command.execute("c", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertEquals("yro1\n", sWriter.toString());
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}

	@Test
	public void testStringMethod() {
		String inputCommand = target + "\nmethod4\nsc\ne\n";
		try {
			command.execute("c", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertEquals("yro1\n", sWriter.toString());
			assertEquals(3,
					((ExampleClass) gateway.getObject("o1")).getField1());
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}

	@Test
	public void testStringMethodWithNull() {
		String inputCommand = target + "\nmethod4\nn\ne\n";
		try {
			command.execute("c", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertEquals("yro1\n", sWriter.toString());
			assertEquals(3,
					((ExampleClass) gateway.getObject("o1")).getField1());
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}

	@Test
	public void testUsingMethodReturn() {
		String inputCommand = target + "\nmethod4\nsc\ne\n";
		String inputCommand2 = target + "\nmethod5\nro1\ne\n";
		try {
			command.execute("c", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertEquals("yro1\n", sWriter.toString());
			command.execute("c", new BufferedReader(new StringReader(
					inputCommand2)), writer);
			assertEquals("yro1\nyi2\n", sWriter.toString());
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}

}
