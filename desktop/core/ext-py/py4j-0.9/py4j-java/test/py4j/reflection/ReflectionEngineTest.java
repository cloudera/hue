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
package py4j.reflection;

import static org.junit.Assert.assertArrayEquals;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertNull;
import static org.junit.Assert.assertTrue;
import static org.junit.Assert.fail;

import java.util.ArrayList;

import org.junit.Before;
import org.junit.Test;

import p1.Cat;

public class ReflectionEngineTest {

	private ReflectionEngine rEngine;

	@Before
	public void setUp() {
		rEngine = new ReflectionEngine();
	}

	@Test
	public void testGetSimpleMethod() {
		assertNull(rEngine.getMethod(Cat.class, "methodABC"));
		assertNotNull(rEngine.getMethod(Cat.class, "meow"));
		assertNotNull(rEngine.getMethod(Cat.class, "meow15"));
	}

	@Test
	public void testGetClass() {
		assertNull(rEngine.getClass(Cat.class, "smallcat"));
		assertNotNull(rEngine.getClass(Cat.class, "SmallCat"));
		assertNull(rEngine.getClass(ReflectionEngineTest.class, "smallcat"));
	}

	@Test
	public void testGetField() {
		Cat cat = new Cat();
		// Private from super
		assertNull(rEngine.getField(cat, "age"));

		// Inexistent
		assertNull(rEngine.getField(cat, "age1"));

		// Field shadowing
		assertEquals(rEngine.getField(cat, "age2").getType(), int.class);
		assertEquals(rEngine.getField(Cat.class, "age2").getType(), int.class);
		assertEquals(rEngine.getField("p1.Cat", "age2").getType(), int.class);

		// Static field
		assertEquals(rEngine.getField(cat, "CONSTANT").getType(), String.class);

		// Package
		assertNull(rEngine.getField(cat, "age4"));

		// Protected
		assertNull(rEngine.getField(cat, "age5"));
	}

	@Test
	public void testCreateArray() {
		Object array1 = rEngine.createArray("int", new int[] { 2 });
		int[] array1int = (int[]) array1;
		assertEquals(2, array1int.length);

		array1 = rEngine.createArray("java.lang.String", new int[] { 3, 4 });
		String[][] array1String = (String[][]) array1;
		assertEquals(3, array1String.length);
		assertEquals(4, array1String[0].length);
	}

	@Test
	public void testGetFieldValue() {
		Cat cat = new Cat();

		assertEquals(rEngine.getFieldValue(cat, rEngine.getField(cat, "age2")),
				2);
		assertEquals(
				rEngine.getFieldValue(cat, rEngine.getField(cat, "CONSTANT")),
				"Salut!");
		assertEquals(
				rEngine.getFieldValue(null, rEngine.getField(cat, "CONSTANT")),
				"Salut!");
	}

	@Test
	public void testGetConstructor() {
		ReflectionEngine engine = new ReflectionEngine();
		MethodInvoker mInvoker = engine.getConstructor("p1.Cat",
				new Object[] {});
		assertArrayEquals(mInvoker.getConstructor().getParameterTypes(),
				new Class[] {});

		// Test cache:
		mInvoker = engine.getConstructor("p1.Cat", new Object[] {});
		assertArrayEquals(mInvoker.getConstructor().getParameterTypes(),
				new Class[] {});

		// Test one only
		mInvoker = engine.getConstructor("p1.Cat",
				new Object[] { new Integer(2) });
		assertArrayEquals(mInvoker.getConstructor().getParameterTypes(),
				new Class[] { int.class });

		// Test cost computation
		mInvoker = engine.getConstructor("p1.Cat", new Object[] {
				new ArrayList<String>(), new String() });
		assertArrayEquals(mInvoker.getConstructor().getParameterTypes(),
				new Class[] { Object.class, String.class });

		mInvoker = engine.getConstructor("p1.Cat", new Object[] { "",
				new String() });
		assertArrayEquals(mInvoker.getConstructor().getParameterTypes(),
				new Class[] { String.class, String.class });

		mInvoker = engine.getConstructor("p1.Cat", new Object[] { "a", 2 });
		assertArrayEquals(mInvoker.getConstructor().getParameterTypes(),
				new Class[] { char.class, int.class });

		mInvoker = engine.getConstructor("p1.Cat", new Object[] { true, 2 });
		assertArrayEquals(mInvoker.getConstructor().getParameterTypes(),
				new Class[] { boolean.class, short.class });

		// Test invokation
		mInvoker = engine.getConstructor("p1.Cat", new Object[] { "a", 2 });
		Object obj = mInvoker.invoke(null, new Object[] { "a", 2 });
		assertTrue(obj instanceof Cat);
	}

	@Test
	public void testGetMethod() {
		try {
			ReflectionEngine engine = new ReflectionEngine();
			TestEngine2 tEngine = new TestEngine2();
			MethodInvoker mInvoker = engine.getMethod(tEngine, "method1",
					new Object[] { new Object(), new Object() });
			assertArrayEquals(mInvoker.getMethod().getParameterTypes(),
					new Class[] { Object.class, Object.class });

			// Test cache:
			mInvoker = engine.getMethod(tEngine, "method1", new Object[] {
					new Object(), new Object() });
			assertArrayEquals(mInvoker.getMethod().getParameterTypes(),
					new Class[] { Object.class, Object.class });

			// Test one only
			mInvoker = engine.getMethod(tEngine, "method2",
					new Object[] { new Object() });
			assertArrayEquals(mInvoker.getMethod().getParameterTypes(),
					new Class[] { Object.class });

			// Test no param
			mInvoker = engine.getMethod(tEngine, "method1", new Object[] {});
			assertArrayEquals(mInvoker.getMethod().getParameterTypes(),
					new Class[] {});

			// Test no match
			try {
				mInvoker = engine.getMethod(tEngine, "method3",
						new Object[] { new Object() });
				fail();
			} catch (Exception e) {
			}

			// Test one invalid
			try {
				mInvoker = engine.getMethod(tEngine, "method2", new Object[] {
						new Object(), new Object() });
				fail();
			} catch (Exception e) {
			}

			// Test many, but invalid
			try {
				mInvoker = engine.getMethod(tEngine, "method1", new Object[] {
						new Object(), new Object(), new Object() });
				fail();
			} catch (Exception e) {
			}

			// Test many
			mInvoker = engine.getMethod(tEngine, "method1", new Object[] {
					new String(), new ArrayList<String>() });
			assertArrayEquals(mInvoker.getMethod().getParameterTypes(),
					new Class[] { String.class, Object.class });

			mInvoker = engine.getMethod(tEngine, "method1", new Object[] {
					new String(), new String() });
			assertArrayEquals(mInvoker.getMethod().getParameterTypes(),
					new Class[] { String.class, char.class });

			mInvoker = engine.getMethod(tEngine, "method1", new Object[] { 2,
					2.2 });
			assertArrayEquals(mInvoker.getMethod().getParameterTypes(),
					new Class[] { int.class, double.class });

			// Two methods are equal. Selected method will depend on how methods
			// are given
			// during reflection.
			mInvoker = engine.getMethod(tEngine, "method1", new Object[] { "2",
					true });
			assertArrayEquals(mInvoker.getMethod().getParameterTypes(),
					new Class[] { Object.class, Boolean.class });
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}

}

class TestEngine {

	public int method1(Object obj1, Object obj2) {
		return 2;
	}

	public void method1(String s1, Object obj2) {

	}

	public boolean method1(String s1, char c2) {
		return true;
	}

	public void method2(Object obj1) {

	}

	public void method1() {

	}
}

class TestEngine2 extends TestEngine {

	public int method1(Object obj1, Object obj2) {
		return 3;
	}

	public void method1(long l1, float f2) {
		// Not reachable because int, double is closer to python than long float
	}

	public void method1(short s1, double d2) {
		// Still unreachable
	}

	public int method1(int i1, double d2) {
		return 2;
	}

	public void method1(Object obj1, Boolean b2) {

	}

}
