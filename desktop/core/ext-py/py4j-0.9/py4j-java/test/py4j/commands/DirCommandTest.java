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
import static org.junit.Assert.assertNull;
import static org.junit.Assert.assertTrue;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.StringReader;
import java.io.StringWriter;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;

import py4j.Gateway;
import py4j.Protocol;
import py4j.examples.ExampleClass;
import py4j.examples.ExampleEntryPoint;

public class DirCommandTest {
	private ExampleEntryPoint entryPoint;
	private Gateway gateway;
	private DirCommand command;
	private BufferedWriter writer;
	private StringWriter sWriter;
	private String target;

	private static Set<String> ExampleClassFields = new HashSet<String>();
	{
		ExampleClassFields.addAll(Arrays.asList(new String[] { "field10",
				"field11", "field20", "field21", "static_field" }));
	}
	private static Set<String> ExampleClassMethods = new HashSet<String>();
	{
		// Defined in ExampleClass
		ExampleClassMethods.addAll(Arrays.asList(new String[] { "method1",
				"method2", "method3", "method4", "method5", "method6",
				"method7", "method8", "method9", "method10", "method11",
				"getList", "getField1", "setField1", "getStringArray",
				"getIntArray", "callHello", "callHello2", "static_method" }));
		// Defined in Object
		ExampleClassMethods.addAll(Arrays
				.asList(new String[] { "getClass", "hashCode", "equals",
						"toString", "notify", "notifyAll", "wait" }));
	}
	private static Set<String> ExampleClassStatics = new HashSet<String>();
	{
		ExampleClassStatics.addAll(Arrays.asList(new String[] { "StaticClass",
				"static_method", "static_field" }));
	}

	@Before
	public void setUp() {
		entryPoint = new ExampleEntryPoint();
		gateway = new Gateway(entryPoint);
		gateway.startup();
		command = new DirCommand();
		command.init(gateway);
		sWriter = new StringWriter();
		writer = new BufferedWriter(sWriter);
		target = gateway.getReturnObject(entryPoint.getNewExample()).getName();
	}

	@After
	public void tearDown() {
		gateway.shutdown();
	}

	@Test
	public void testDirFields() throws Exception {
		String inputCommand = "f\n" + target + "\ne\n";

		assertTrue(gateway.getBindings().containsKey(target));
		command.execute("d",
				new BufferedReader(new StringReader(inputCommand)), writer);
		Set<String> fields = convertResponse(sWriter.toString());
		assertEquals(ExampleClassFields, fields);
	}

	@Test
	public void testDirMethods() throws Exception {
		String inputCommand = "m\n" + target + "\ne\n";

		assertTrue(gateway.getBindings().containsKey(target));
		command.execute("d",
				new BufferedReader(new StringReader(inputCommand)), writer);
		Set<String> methods = convertResponse(sWriter.toString());
		assertEquals(ExampleClassMethods, methods);
	}

	@Test
	public void testDirStatics() throws Exception {
		String inputCommand = "s\n" + ExampleClass.class.getName() + "\ne\n";

		assertTrue(gateway.getBindings().containsKey(target));
		command.execute("d",
				new BufferedReader(new StringReader(inputCommand)), writer);
		Set<String> methods = convertResponse(sWriter.toString());
		assertEquals(ExampleClassStatics, methods);
	}

	private String createDirJvmViewCommand(String sequenceId) {
		if (sequenceId == null) {
			return "v\nr" + Protocol.DEFAULT_JVM_OBJECT_ID + "\nn\ne\n";
		} else {
			return "v\nr" + Protocol.DEFAULT_JVM_OBJECT_ID + "\ns" + sequenceId
					+ "\ne\n";
		}
	}

	@Test
	public void testDirJvmView() throws Exception {
		assertTrue(gateway.getBindings().containsKey(target));

		// Initial case, empty contents
		command.execute("d", new BufferedReader(new StringReader(
				createDirJvmViewCommand(null))), writer);
		JvmViewRet result = convertResponseJvmView(sWriter.toString());
		sWriter.getBuffer().setLength(0);
		assertEquals(new HashSet<String>(), result.names);

		// Initial case, non-empty contents
		gateway.getDefaultJVMView().addSingleImport("com.example.Class1");
		gateway.getDefaultJVMView().addSingleImport("com.another.Class2");
		command.execute("d", new BufferedReader(new StringReader(
				createDirJvmViewCommand(null))), writer);
		result = convertResponseJvmView(sWriter.toString());
		sWriter.getBuffer().setLength(0);
		String sequenceID = result.sequenceId;
		assertEquals(new HashSet<String>(Arrays.asList("Class1", "Class2")),
				result.names);

		// Read again with sequence # we just received
		command.execute("d", new BufferedReader(new StringReader(
				createDirJvmViewCommand(sequenceID))), writer);
		result = convertResponseJvmView(sWriter.toString());
		sWriter.getBuffer().setLength(0);
		assertNull(result);

		// Add another with sequence # we received
		gateway.getDefaultJVMView().addSingleImport("com.third.Class3");
		command.execute("d", new BufferedReader(new StringReader(
				createDirJvmViewCommand(sequenceID))), writer);
		result = convertResponseJvmView(sWriter.toString());
		sWriter.getBuffer().setLength(0);
		assertEquals(
				new HashSet<String>(Arrays.asList("Class1", "Class2", "Class3")),
				result.names);
	}

	private Set<String> convertResponse(String protocolReturn) {
		assertTrue(protocolReturn.startsWith("y"));
		String fieldsJoined = (String) Protocol.getObject(
				protocolReturn.substring(1), gateway);
		return new HashSet<String>(Arrays.asList(fieldsJoined.split("\n")));
	}

	class JvmViewRet {
		String sequenceId;
		Set<String> names;
	}

	private JvmViewRet convertResponseJvmView(String protocolReturn) {
		assertTrue(protocolReturn.startsWith("y"));
		String fieldsJoined = (String) Protocol.getObject(
				protocolReturn.substring(1), gateway);
		if (fieldsJoined == null) {
			return null;
		}
		List<String> list = Arrays.asList(fieldsJoined.split("\n"));
		assertTrue(list.size() >= 1);
		JvmViewRet ret = new JvmViewRet();
		ret.sequenceId = list.get(0);
		ret.names = new HashSet<String>();
		ret.names.addAll(list.subList(1, list.size()));
		return ret;
	}
}
