/*******************************************************************************
 * Copyright (c) 2010, 2011, Barthelemy Dagenais All rights reserved.
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
import py4j.examples.ExampleEntryPoint;
import py4j.examples.Stack;

public class ConstructorCommandTest {
	private ExampleEntryPoint entryPoint;
	private Gateway gateway;
	private ConstructorCommand command;
	private BufferedWriter writer;
	private StringWriter sWriter;

	@Before
	public void setUp() {
		entryPoint = new ExampleEntryPoint();
		gateway = new Gateway(entryPoint);
		gateway.startup();
		command = new ConstructorCommand();
		command.init(gateway);
		sWriter = new StringWriter();
		writer = new BufferedWriter(sWriter);
	}

	@After
	public void tearDown() {
		gateway.shutdown();
	}

	@Test
	public void testConstructor0Arg() {
		String inputCommand = "py4j.examples.ExampleClass\ne\n";
		try {
			command.execute("i", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertEquals("yro0\n", sWriter.toString());
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}

	@Test
	public void testConstructor1Arg() {
		String inputCommand = "py4j.examples.ExampleClass\ni5\ne\n";
		try {
			command.execute("i", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertEquals("yro0\n", sWriter.toString());
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}

	@Test
	public void testDefaultConstructor() {
		String inputCommand = "py4j.examples.Stack\ne\n";
		try {
			command.execute("i", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertEquals("yro0\n", sWriter.toString());
			assertTrue(gateway.getObject("o0") instanceof Stack);
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}

	@Test
	public void testWrongConstructor() {
		String inputCommand = "py4j.examples.Stack\ni5\ne\n";
		try {
			command.execute("i", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertTrue(sWriter.toString().startsWith("x"));
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}
}
