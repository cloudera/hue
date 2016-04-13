/**
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
 */

package py4j;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;
import static org.junit.Assert.fail;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;

import py4j.commands.Command;
import py4j.examples.ExampleClass;
import py4j.examples.ExampleEntryPoint;

public class GatewayTest {

	private Gateway gateway;
	private ExampleEntryPoint entryPoint;

	@Before
	public void setUp() {
		entryPoint = new ExampleEntryPoint();
		gateway = new Gateway(entryPoint);
	}

	@After
	public void tearDown() {
		gateway.shutdown();
	}

	@Test
	public void testNoParam() {
		String name = gateway.putNewObject(entryPoint.getNewExample());
		ReturnObject obj2 = gateway.invoke("method1", name, null);
		assertEquals(1, obj2.getPrimitiveObject());
	}

	@Test
	public void testVoidMethod() {
		String name = gateway.putNewObject(entryPoint.getNewExample());
		List<Object> args = new ArrayList<Object>();
		args.add(new String("This is a String!"));
		ReturnObject obj2 = gateway.invoke("method2", name, args);
		assertTrue(obj2.isVoid());
	}

	@Test
	public void testMethodWithParams() {
		String name = gateway.putNewObject(entryPoint.getNewExample());
		List<Object> args = new ArrayList<Object>();
		args.add(new Integer(1));
		args.add(new Boolean(false));
		ReturnObject obj2 = gateway.invoke("method3", name, args);
		assertEquals("Hello World", obj2.getPrimitiveObject());
	}

	@Test
	public void testCharMethod() {
		String name = gateway.putNewObject(entryPoint.getNewExample());
		List<Object> args = new ArrayList<Object>();
		args.add(new Character('c'));
		ReturnObject obj2 = gateway.invoke("method4", name, args);

		// In practice, the argument is a string when it comes from python
		// So String parameters ALWAYS hide chars.
		assertEquals(1,
				((ExampleClass) gateway.getObject(obj2.getName())).getField1());
	}

	@Test
	public void testCharMethod2() {
		String name = gateway.putNewObject(entryPoint.getNewExample());
		List<Object> args = new ArrayList<Object>();
		args.add(new Character('c'));
		ReturnObject obj2 = gateway.invoke("method6", name, args);
		assertEquals(4,
				((ExampleClass) gateway.getObject(obj2.getName())).getField1());
	}

	@Test
	public void testStringMethod() {
		String name = gateway.putNewObject(entryPoint.getNewExample());
		List<Object> args = new ArrayList<Object>();
		args.add(new String("c"));
		ReturnObject obj2 = gateway.invoke("method4", name, args);
		assertEquals(3,
				((ExampleClass) gateway.getObject(obj2.getName())).getField1());
	}

	@Test
	public void testUsingMethodReturn() {
		String name = gateway.putNewObject(entryPoint.getNewExample());
		List<Object> args = new ArrayList<Object>();
		args.add(new String("c"));
		ReturnObject obj2 = gateway.invoke("method4", name, args);
		args = new ArrayList<Object>();
		args.add(gateway.getObject(obj2.getName()));
		ReturnObject obj3 = gateway.invoke("method5", name, args);
		assertEquals(2, obj3.getPrimitiveObject());
	}

	@SuppressWarnings("unchecked")
	@Test
	public void testListMethod() {
		String name = gateway.putNewObject(entryPoint.getNewExample());
		List<Object> args = new ArrayList<Object>();
		args.add(new Integer(3));
		ReturnObject obj2 = gateway.invoke("getList", name, args);
		List<String> myList = (List<String>) gateway.getObject(obj2.getName());
		assertEquals(myList.size(), 3);

		args = new ArrayList<Object>();
		args.add(new String("\"3\""));
		gateway.invoke("add", obj2.getName(), args);
		assertEquals(myList.size(), 4);
	}

	@Test
	public void testUniqueCommands() {
		Set<String> commandNames = new HashSet<String>();
		try {
			for (Class<? extends Command> clazz : GatewayConnection
					.getBaseCommands()) {
				Command command = clazz.newInstance();
				String commandName = command.getCommandName();
				if (commandNames.contains(commandName)) {
					fail("Duplicate command name " + commandName);
				} else {
					commandNames.add(commandName);
				}
			}
		} catch (Exception e) {
			fail();
		}
	}

}
