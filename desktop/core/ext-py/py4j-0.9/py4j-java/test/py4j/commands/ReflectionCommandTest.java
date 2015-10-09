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
import py4j.examples.ExampleEntryPoint;

public class ReflectionCommandTest {
	private Gateway gateway;
	private ReflectionCommand command;
	private BufferedWriter writer;
	private StringWriter sWriter;

	@Before
	public void setUp() {
		gateway = new Gateway(new ExampleEntryPoint());
		gateway.startup();
		command = new ReflectionCommand();
		command.init(gateway);
		sWriter = new StringWriter();
		writer = new BufferedWriter(sWriter);

	}

	@After
	public void tearDown() {
		gateway.shutdown();
	}

	@Test
	public void testUnknown() {
		String inputCommand1 = ReflectionCommand.GET_UNKNOWN_SUB_COMMAND_NAME
				+ "\n" + "java" + "\nrj\ne\n";
		String inputCommand2 = ReflectionCommand.GET_UNKNOWN_SUB_COMMAND_NAME
				+ "\n" + "java.lang" + "\nrj\ne\n";
		String inputCommand3 = ReflectionCommand.GET_UNKNOWN_SUB_COMMAND_NAME
				+ "\n" + "java.lang.String" + "\nrj\ne\n";
		String inputCommand4 = ReflectionCommand.GET_UNKNOWN_SUB_COMMAND_NAME
				+ "\n" + "p1.Cat" + "\nrj\ne\n";
		String inputCommand5 = ReflectionCommand.GET_UNKNOWN_SUB_COMMAND_NAME
				+ "\n" + "byte" + "\nrj\ne\n";
		String inputCommand6 = ReflectionCommand.GET_UNKNOWN_SUB_COMMAND_NAME
				+ "\n" + "System" + "\nrj\ne\n";
		String inputCommand7 = ReflectionCommand.GET_UNKNOWN_SUB_COMMAND_NAME
				+ "\n" + "File" + "\nrj\ne\n";
		try {
			this.gateway.getDefaultJVMView().addSingleImport("java.util.List");
			this.gateway.getDefaultJVMView().addStarImport("java.io.*");
			command.execute("r", new BufferedReader(new StringReader(
					inputCommand1)), writer);
			assertEquals("yp\n", sWriter.toString());
			command.execute("r", new BufferedReader(new StringReader(
					inputCommand2)), writer);
			assertEquals("yp\nyp\n", sWriter.toString());
			command.execute("r", new BufferedReader(new StringReader(
					inputCommand3)), writer);
			assertEquals("yp\nyp\nycjava.lang.String\n", sWriter.toString());
			command.execute("r", new BufferedReader(new StringReader(
					inputCommand4)), writer);
			assertEquals("yp\nyp\nycjava.lang.String\nycp1.Cat\n",
					sWriter.toString());
			command.execute("r", new BufferedReader(new StringReader(
					inputCommand5)), writer);
			assertEquals("yp\nyp\nycjava.lang.String\nycp1.Cat\nycbyte\n",
					sWriter.toString());
			command.execute("r", new BufferedReader(new StringReader(
					inputCommand6)), writer);
			assertEquals(
					"yp\nyp\nycjava.lang.String\nycp1.Cat\nycbyte\nycjava.lang.System\n",
					sWriter.toString());
			command.execute("r", new BufferedReader(new StringReader(
					inputCommand7)), writer);
			assertEquals(
					"yp\nyp\nycjava.lang.String\nycp1.Cat\nycbyte\nycjava.lang.System\nycjava.io.File\n",
					sWriter.toString());

		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}

	@Test
	public void testMember() {
		String inputCommand1 = ReflectionCommand.GET_MEMBER_SUB_COMMAND_NAME
				+ "\n" + "java.lang.String\n" + "valueOf" + "\ne\n";
		String inputCommand2 = ReflectionCommand.GET_MEMBER_SUB_COMMAND_NAME
				+ "\n" + "java.lang.String\n" + "length" + "\ne\n";
		String inputCommand3 = ReflectionCommand.GET_MEMBER_SUB_COMMAND_NAME
				+ "\n" + "p1.Cat\n" + "meow" + "\ne\n";
		String inputCommand4 = ReflectionCommand.GET_MEMBER_SUB_COMMAND_NAME
				+ "\n" + "p1.Cat\n" + "meow20" + "\ne\n"; // does not exist
		String inputCommand5 = ReflectionCommand.GET_MEMBER_SUB_COMMAND_NAME
				+ "\n" + "p1.Cat\n" + "meow15" + "\ne\n";
		String inputCommand6 = ReflectionCommand.GET_MEMBER_SUB_COMMAND_NAME
				+ "\n" + "p1.Cat\n" + "CONSTANT" + "\ne\n";
		try {
			command.execute("r", new BufferedReader(new StringReader(
					inputCommand1)), writer);
			assertEquals("ym\n", sWriter.toString());
			command.execute("r", new BufferedReader(new StringReader(
					inputCommand2)), writer);
			assertEquals(
					"ym\nxsTrying to access a non-static member from a static context.\n",
					sWriter.toString());
			command.execute("r", new BufferedReader(new StringReader(
					inputCommand3)), writer);
			assertEquals(
					"ym\nxsTrying to access a non-static member from a static context.\nxsTrying to access a non-static member from a static context.\n",
					sWriter.toString());
			command.execute("r", new BufferedReader(new StringReader(
					inputCommand4)), writer);
			assertEquals(
					"ym\nxsTrying to access a non-static member from a static context.\nxsTrying to access a non-static member from a static context.\nx\n",
					sWriter.toString());
			command.execute("r", new BufferedReader(new StringReader(
					inputCommand5)), writer);
			assertEquals(
					"ym\nxsTrying to access a non-static member from a static context.\nxsTrying to access a non-static member from a static context.\nx\nym\n",
					sWriter.toString());
			command.execute("r", new BufferedReader(new StringReader(
					inputCommand6)), writer);
			assertEquals(
					"ym\nxsTrying to access a non-static member from a static context.\nxsTrying to access a non-static member from a static context.\nx\nym\nysSalut!\n",
					sWriter.toString());
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}

	}
}
