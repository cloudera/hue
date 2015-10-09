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
import static org.junit.Assert.assertFalse;
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
import py4j.JVMView;
import py4j.examples.ExampleEntryPoint;

public class JVMViewCommandTest {
	private Gateway gateway;
	private JVMViewCommand command;
	private BufferedWriter writer;
	private StringWriter sWriter;

	@Before
	public void setUp() {
		gateway = new Gateway(new ExampleEntryPoint());
		gateway.startup();
		command = new JVMViewCommand();
		command.init(gateway);
		sWriter = new StringWriter();
		writer = new BufferedWriter(sWriter);

	}

	@After
	public void tearDown() {
		gateway.shutdown();
	}

	@Test
	public void testSubCommands() {
		String inputCommand1 = JVMViewCommand.CREATE_VIEW_SUB_COMMAND_NAME
				+ "\n" + "custom" + "\ne\n";
		String inputCommand2 = JVMViewCommand.IMPORT_SUB_COMMAND_NAME
				+ "\nro0\n" + "java.util.*" + "\ne\n";
		String inputCommand3 = JVMViewCommand.IMPORT_SUB_COMMAND_NAME
				+ "\nro0\n" + "java.io.File" + "\ne\n";
		String inputCommand4 = JVMViewCommand.REMOVE_IMPORT_SUB_COMMAND_NAME
				+ "\nro0\n" + "java.io.File" + "\ne\n";
		String inputCommand5 = JVMViewCommand.REMOVE_IMPORT_SUB_COMMAND_NAME
				+ "\nro0\n" + "java.lang.*" + "\ne\n";
		String inputCommand6 = JVMViewCommand.IMPORT_SUB_COMMAND_NAME
				+ "\nrj\n" + "java.util.*" + "\ne\n";
		try {
			command.execute("r", new BufferedReader(new StringReader(
					inputCommand1)), writer);
			assertEquals("yro0\n", sWriter.toString());
			JVMView view = (JVMView) gateway.getObject("o0");

			command.execute("r", new BufferedReader(new StringReader(
					inputCommand2)), writer);
			assertEquals("yro0\nyv\n", sWriter.toString());
			assertEquals(2, view.getStarImports().size()); // 1 for java.lang, 1
															// for java.util
			assertTrue(view.getStarImports().contains("java.util"));

			command.execute("r", new BufferedReader(new StringReader(
					inputCommand3)), writer);
			assertEquals("yro0\nyv\nyv\n", sWriter.toString());
			assertTrue(view.getSingleImportsMap().containsKey("File"));
			assertEquals(1, view.getSingleImportsMap().size()); // 1 for
																// java.io.File

			// Duplicate
			command.execute("r", new BufferedReader(new StringReader(
					inputCommand2)), writer);
			assertEquals("yro0\nyv\nyv\nyv\n", sWriter.toString());
			assertEquals(2, view.getStarImports().size());

			command.execute("r", new BufferedReader(new StringReader(
					inputCommand3)), writer);
			assertEquals("yro0\nyv\nyv\nyv\nyv\n", sWriter.toString());
			assertTrue(view.getSingleImportsMap().containsKey("File"));
			assertEquals(1, view.getSingleImportsMap().size()); // 1 for
																// java.io.File

			command.execute("r", new BufferedReader(new StringReader(
					inputCommand4)), writer);
			assertEquals("yro0\nyv\nyv\nyv\nyv\nybtrue\n", sWriter.toString());
			assertFalse(view.getSingleImportsMap().containsKey("File"));
			assertEquals(0, view.getSingleImportsMap().size()); // 1 for
																// java.io.File

			command.execute("r", new BufferedReader(new StringReader(
					inputCommand4)), writer);
			assertEquals("yro0\nyv\nyv\nyv\nyv\nybtrue\nybfalse\n",
					sWriter.toString());
			assertFalse(view.getSingleImportsMap().containsKey("File"));
			assertEquals(0, view.getSingleImportsMap().size()); // 1 for
																// java.io.File

			command.execute("r", new BufferedReader(new StringReader(
					inputCommand5)), writer);
			assertEquals("yro0\nyv\nyv\nyv\nyv\nybtrue\nybfalse\nybtrue\n",
					sWriter.toString());
			assertFalse(view.getStarImports().contains("java.lang.*"));
			assertEquals(1, view.getStarImports().size()); // 1 for java.io.File

			command.execute("r", new BufferedReader(new StringReader(
					inputCommand5)), writer);
			assertEquals(
					"yro0\nyv\nyv\nyv\nyv\nybtrue\nybfalse\nybtrue\nybfalse\n",
					sWriter.toString());
			assertFalse(view.getStarImports().contains("java.lang.*"));
			assertEquals(1, view.getStarImports().size()); // 1 for java.io.File

			command.execute("r", new BufferedReader(new StringReader(
					inputCommand6)), writer);
			assertEquals(
					"yro0\nyv\nyv\nyv\nyv\nybtrue\nybfalse\nybtrue\nybfalse\nyv\n",
					sWriter.toString());
			assertFalse(gateway.getDefaultJVMView().getStarImports()
					.contains("java.util.*"));
			assertEquals(2, gateway.getDefaultJVMView().getStarImports().size()); // 1
																					// for
																					// java.io.File
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}
}
