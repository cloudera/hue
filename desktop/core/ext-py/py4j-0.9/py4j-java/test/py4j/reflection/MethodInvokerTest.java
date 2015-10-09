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
package py4j.reflection;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertNull;
import static org.junit.Assert.assertTrue;
import static org.junit.Assert.fail;

import java.lang.reflect.Method;

import org.junit.Test;

import p1.Cat;

public class MethodInvokerTest {

	@Test
	public void testInvoke() {
		Cat cat = new Cat();
		try {
			Method m = Cat.class.getMethod("meow10", float.class);
			MethodInvoker invoker = new MethodInvoker(m,
					new TypeConverter[] { new TypeConverter(
							TypeConverter.DOUBLE_TO_FLOAT) }, 0);
			invoker.invoke(cat, new Object[] { new Double(2.0) });

			m = Cat.class.getMethod("meow11", new Class[0]);
			invoker = new MethodInvoker(m, null, 0);
			invoker.invoke(cat, new Object[0]);

			m = Cat.class.getMethod("meow10", float.class);
			invoker = new MethodInvoker(m, null, 0);
			invoker.invoke(cat, new Object[] { new Float(1.1f) });
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}

	@Test
	public void testVoid() {
		try {
			Method m = Cat.class.getMethod("meow10", float.class);
			MethodInvoker invoker = new MethodInvoker(m,
					new TypeConverter[] { new TypeConverter(
							TypeConverter.DOUBLE_TO_FLOAT) }, 0);
			assertTrue(invoker.isVoid());

			m = Cat.class.getMethod("meow12", new Class[0]);
			invoker = new MethodInvoker(m, null, 0);
			assertFalse(invoker.isVoid());
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}

	@Test
	public void testBuildInvokerFloat() {
		try {
			Method m = Cat.class.getMethod("meow10", float.class);
			MethodInvoker invoker1 = MethodInvoker.buildInvoker(m,
					new Class[] { float.class });
			assertEquals(0, invoker1.getCost());
			invoker1 = MethodInvoker.buildInvoker(m,
					new Class[] { Float.class });
			assertEquals(0, invoker1.getCost());
			assertNull(invoker1.getConverters());
			invoker1 = MethodInvoker.buildInvoker(m,
					new Class[] { Double.class });
			assertEquals(1, invoker1.getCost());
			assertNotNull(invoker1.getConverters());

			Cat cat = new Cat();
			assertNull(invoker1.invoke(cat, new Object[] { 2.0 }));
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}

	@Test
	public void testBuildInvokerAll() {
		try {
			Cat cat = new Cat();
			Method m = Cat.class.getMethod("meow13", long.class, int.class,
					short.class, byte.class, double.class, Float.class,
					boolean.class, String.class, char.class);

			Method m2 = Cat.class.getMethod("meow14", Long.class, int.class,
					short.class, byte.class, double.class, Float.class,
					boolean.class, String.class, char.class);

			MethodInvoker invoker = MethodInvoker.buildInvoker(m, new Class[] {
					long.class, int.class, short.class, byte.class,
					double.class, float.class, boolean.class, String.class,
					char.class });
			assertEquals(0, invoker.getCost());
			assertNull(invoker.getConverters());

			// Distance greater than 0, but only long conversion required.
			invoker = MethodInvoker
					.buildInvoker(m, new Class[] { int.class, byte.class,
							short.class, byte.class, Float.class, float.class,
							Boolean.class, String.class, Character.class });
			assertEquals(4, invoker.getCost());
			assertEquals(9, invoker.getConverters().length);
			assertEquals(TypeConverter.NUM_TO_LONG,
					invoker.getConverters()[0].getConversion());

			// Distance greater than 0, but only long conversion required.
			invoker = MethodInvoker
					.buildInvoker(m2, new Class[] { int.class, byte.class,
							short.class, byte.class, Float.class, float.class,
							Boolean.class, String.class, Character.class });
			assertEquals(4, invoker.getCost());
			assertEquals(9, invoker.getConverters().length);
			assertEquals(TypeConverter.NUM_TO_LONG,
					invoker.getConverters()[0].getConversion());

			// Invalid.
			invoker = MethodInvoker
					.buildInvoker(m, new Class[] { double.class, byte.class,
							short.class, byte.class, Float.class, float.class,
							Boolean.class, String.class, Character.class });
			assertEquals(-1, invoker.getCost());
			assertNull(invoker.getConverters());

			// Need char conversion
			invoker = MethodInvoker.buildInvoker(m, new Class[] { long.class,
					int.class, short.class, byte.class, double.class,
					float.class, boolean.class, String.class, String.class });
			assertEquals(1, invoker.getCost());
			assertEquals(9, invoker.getConverters().length);
			assertEquals(
					10,
					invoker.invoke(cat, new Object[] { 1l, 2, (short) 3,
							(byte) 4, 1.2, 1.2f, true, "a", "a" }));

			// Need short, byte conversion
			invoker = MethodInvoker.buildInvoker(m, new Class[] { long.class,
					int.class, Integer.class, int.class, double.class,
					float.class, boolean.class, String.class, char.class });
			assertEquals(3, invoker.getCost());
			assertEquals(9, invoker.getConverters().length);
			assertEquals(
					10,
					invoker.invoke(cat, new Object[] { 1l, 2, 3, 4, 1.2, 1.2f,
							true, "a", 'a' }));
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}

	@Test
	public void testBuildInvokerObject() {
		try {
			TestInvoker tInvoker = new TestInvoker();
			Method m = TestInvoker.class.getMethod("m1", ATest.class,
					VTest.class, I0Test.class, J0Test.class);

			MethodInvoker invoker = MethodInvoker.buildInvoker(m, new Class[] {
					ATest.class, VTest.class, I0Test.class, J0Test.class });
			assertEquals(0, invoker.getCost());
			assertNull(invoker.getConverters());
			assertNull(invoker.invoke(tInvoker, new Object[] { new ATest(),
					new VTest(), new I0Test() {
					}, new J0Test() {
					} }));

			invoker = MethodInvoker.buildInvoker(m, new Class[] { BTest.class,
					WTest.class, I2Test.class, J0Test.class });
			assertEquals(400, invoker.getCost());
			assertNull(invoker.getConverters());
			assertNull(invoker.invoke(tInvoker, new Object[] { new BTest(),
					new WTest(), new I2Test() {
					}, new J0Test() {
					} }));

			m = TestInvoker.class.getMethod("m2", String.class, Object.class);
			invoker = MethodInvoker.buildInvoker(m, new Class[] { String.class,
					String.class });
			assertEquals(100, invoker.getCost());
			assertNull(invoker.getConverters());
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}

}

class TestInvoker {
	public void m1(ATest a, VTest v, I0Test i0, J0Test j0) {

	}

	public void m2(String s1, Object o1) {

	}
}
