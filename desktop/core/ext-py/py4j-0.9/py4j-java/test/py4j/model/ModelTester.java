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
package py4j.model;

import static org.junit.Assert.assertEquals;

import org.junit.Test;

import p1.AnObject;
import p1.AnObject2;
import p1.AnObject3;
import p1.AnObject4;

public class ModelTester {

	@Test
	public void testModel() {
		Py4JClass clazz = Py4JClass.buildClass(AnObject.class, true);
		assertEquals(clazz.getSignature(false), "p1.AnObject");
		assertEquals(clazz.getSignature(true), "AnObject");
		assertEquals(1, clazz.getClasses().length);
		assertEquals(2, clazz.getMethods().length);
		assertEquals(1, clazz.getFields().length);
		Py4JMethod m1 = clazz.getMethods()[0];
		Py4JMethod m2 = clazz.getMethods()[1];
		Py4JField f1 = clazz.getFields()[0];
		Py4JClass clazz2 = clazz.getClasses()[0];
		assertEquals(m1.getSignature(false),
				"m1(java.lang.String, p1.AnObject) : void");
		assertEquals(m1.getSignature(true), "m1(String, AnObject) : void");
		assertEquals(m2.getSignature(false), "m2(int) : java.lang.String");
		assertEquals(m2.getSignature(true), "m2(int) : String");
		assertEquals(f1.getSignature(false), "value1 : java.lang.Integer");
		assertEquals(f1.getSignature(true), "value1 : Integer");
		assertEquals(clazz2.getSignature(false), "p1.AnObject.InternalClass");
		assertEquals(clazz2.getSignature(true), "InternalClass");
	}

	@Test
	public void testClassWithSuper() {
		Py4JClass clazz2 = Py4JClass.buildClass(AnObject2.class, true);
		Py4JClass clazz3 = Py4JClass.buildClass(AnObject3.class, true);
		Py4JClass clazz4 = Py4JClass.buildClass(AnObject4.class, true);

		assertEquals(clazz2.getSignature(false),
				"p1.AnObject2 extends p1.AnObject");
		assertEquals(clazz3.getSignature(false),
				"p1.AnObject3 implements java.lang.Runnable, java.io.Serializable");
		assertEquals(clazz4.getSignature(false),
				"p1.AnObject4 extends p1.AnObject3 implements java.lang.Cloneable");
	}

	@Test
	public void testClassHelpPage() {
		// This is manual testing, to see how it will look like.
		Py4JClass clazz = Py4JClass.buildClass(AnObject.class, true);
		String helpPage = HelpPageGenerator.getHelpPage(clazz, null, false);
		System.out.println("BEGIN");
		System.out.println(helpPage);
		System.out.println("END");

		helpPage = HelpPageGenerator.getHelpPage(clazz, null, true);
		System.out.println("BEGIN");
		System.out.println(helpPage);
		System.out.println("END");
	}

	@Test
	public void testMethodHelpPage() {
		// This is manual testing, to see how it will look like.
		Py4JClass clazz = Py4JClass.buildClass(AnObject.class, true);
		String helpPage = HelpPageGenerator.getHelpPage(clazz.getMethods()[0],
				false);
		System.out.println("BEGIN");
		System.out.println(helpPage);
		System.out.println("END");
	}
}
