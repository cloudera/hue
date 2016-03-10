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
import static org.junit.Assert.fail;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.StringReader;
import java.io.StringWriter;
import java.lang.reflect.Array;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;

import py4j.Gateway;
import py4j.Protocol;
import py4j.ReturnObject;
import py4j.examples.ExampleEntryPoint;

public class ArrayCommandTest {
	private Gateway gateway;
	private ArrayCommand command;
	private BufferedWriter writer;
	private StringWriter sWriter;
	private String target;
	private String target2;
	private Object array1;
	private Object array2;

	@Before
	public void setUp() {
		gateway = new Gateway(new ExampleEntryPoint());
		gateway.startup();
		command = new ArrayCommand();
		command.init(gateway);
		sWriter = new StringWriter();
		writer = new BufferedWriter(sWriter);
		array1 = new String[] { "222", "111" };
		array2 = new int[] { 2, 1 };
		target = gateway.putNewObject(array1);
		target2 = gateway.putNewObject(array2);
	}

	@After
	public void tearDown() {
		gateway.shutdown();
	}

	@Test
	public void testGet() {
		String inputCommand = ArrayCommand.ARRAY_GET_SUB_COMMAND_NAME + "\n"
				+ target + "\ni1\ne\n";
		try {
			command.execute("a", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertEquals("ys111\n", sWriter.toString());
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}

	@Test
	public void testSet() {
		String inputCommand = ArrayCommand.ARRAY_SET_SUB_COMMAND_NAME + "\n"
				+ target2 + "\ni1\ni555\ne\n";
		try {
			command.execute("a", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertEquals("yv\n", sWriter.toString());
			assertEquals(Array.getInt(array2, 1), 555);
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}

	@Test
	public void testLength() {
		String inputCommand = ArrayCommand.ARRAY_LEN_SUB_COMMAND_NAME + "\n"
				+ target + "\ne\n";
		try {
			command.execute("a", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertEquals("yi2\n", sWriter.toString());
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}

	@Test
	public void testCreateArray() {
		String inputCommand = ArrayCommand.ARRAY_CREATE_SUB_COMMAND_NAME
				+ "\nsint\ni3\ne\n";
		try {
			command.execute("a", new BufferedReader(new StringReader(
					inputCommand)), writer);
			int[] intarray = (int[]) gateway.getObject("o2");
			assertEquals(3, intarray.length);

			inputCommand = ArrayCommand.ARRAY_CREATE_SUB_COMMAND_NAME
					+ "\nsjava.lang.String\ni3\ni5\ne\n";
			command.execute("a", new BufferedReader(new StringReader(
					inputCommand)), writer);
			String[][] stringarray = (String[][]) gateway.getObject("o3");
			assertEquals(3, stringarray.length);
			assertEquals(5, stringarray[0].length);
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}

	@Test
	public void testSlice() {
		int[] array3 = new int[] { 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 };
		String[][] array4 = new String[][] { { "111", "222" },
				{ "aaa", "bbb" }, { "88", "99" } };
		gateway.putNewObject(array3);
		gateway.putNewObject(array4);
		String inputCommand = ArrayCommand.ARRAY_SLICE_SUB_COMMAND_NAME + "\n"
				+ "o2" + "\ni1\ni5\ne\n";
		try {
			command.execute("a", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertEquals("yto4\n", sWriter.toString());
			int[] intarray = (int[]) gateway.getObject("o4");
			assertEquals(2, intarray.length);
			assertEquals(6, intarray[1]);

			inputCommand = ArrayCommand.ARRAY_SLICE_SUB_COMMAND_NAME + "\n"
					+ "o3" + "\ni2\ne\n";
			command.execute("a", new BufferedReader(new StringReader(
					inputCommand)), writer);
			assertEquals("yto4\nyto5\n", sWriter.toString());
			String[][] stringarray = (String[][]) gateway.getObject("o5");
			assertEquals(1, stringarray.length);
			assertEquals("99", stringarray[0][1]);
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}

	}

	@Test
	public void testArrayType() {
		ReturnObject rObject = ReturnObject.getArrayReturnObject(target, 2);
		assertEquals("yt" + target + "\n", Protocol.getOutputCommand(rObject));
	}
}
