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

public class FieldCommandTest {
	private ExampleEntryPoint entryPoint;
	private Gateway gateway;
	private FieldCommand command;
	private BufferedWriter writer;
	private StringWriter sWriter;
	private String target;

	@Before
	public void setUp() {
		entryPoint = new ExampleEntryPoint();
		gateway = new Gateway(entryPoint);
		gateway.startup();
		command = new FieldCommand();
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
	public void testPrivateMember() {
		String inputCommand = "g\n" + target + "\nfield1\ne\n";
		try {
			command.execute("f", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertEquals("yo\n", sWriter.toString());
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}

	@Test
	public void testNoMember() {
		String inputCommand = "g\n" + target + "\nfield2\ne\n";
		try {
			command.execute("f", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertEquals("yo\n", sWriter.toString());
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}

	@Test
	public void testPrimitive() {
		String inputCommand = "g\n" + target + "\nfield10\ne\n";
		try {
			command.execute("f", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertEquals("yi10\n", sWriter.toString());
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}

	@Test
	public void testObject() {
		String inputCommand = "g\n" + target + "\nfield20\ne\n";
		try {
			command.execute("f", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertEquals("yro1\n", sWriter.toString());
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}

	@Test
	public void testNull() {
		String inputCommand = "g\n" + target + "\nfield21\ne\n";
		try {
			command.execute("f", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertEquals("yn\n", sWriter.toString());
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}

	@Test
	public void testSetField() {
		String inputCommand = "s\n" + target + "\nfield10\ni123\ne\n";
		try {
			command.execute("f", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertEquals("yv\n", sWriter.toString());
			assertEquals(((ExampleClass) gateway.getObject(target)).field10,
					123);
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}

	@Test
	public void testSetNoField() {
		String inputCommand = "s\n" + target + "\nfield1\ni123\ne\n";
		try {
			command.execute("f", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertEquals("yo\n", sWriter.toString());
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}

	@Test
	public void testSetFieldObject() {
		String objectId = gateway.putNewObject(new StringBuffer("Hello"));
		String inputCommand = "s\n" + target + "\nfield20\nr" + objectId
				+ "\ne\n";
		try {
			command.execute("f", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertEquals("yv\n", sWriter.toString());
			assertEquals(((ExampleClass) gateway.getObject(target)).field20,
					gateway.getObject(objectId));
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}
}
