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
import static org.junit.Assert.assertTrue;
import static org.junit.Assert.assertFalse;

import org.junit.Test;

public class TypeUtilTest {

	@Test
	public void testDistance() {
		assertEquals(0, TypeUtil.computeDistance(ATest.class, ATest.class));
		assertEquals(100, TypeUtil.computeDistance(ATest.class, BTest.class));
		assertEquals(200, TypeUtil.computeDistance(ATest.class, CTest.class));
		assertEquals(300, TypeUtil.computeDistance(ATest.class, DTest.class));
		assertEquals(400, TypeUtil.computeDistance(Object.class, DTest.class));
		assertEquals(-1, TypeUtil.computeDistance(int.class, DTest.class));
		assertEquals(-1, TypeUtil.computeDistance(String.class, DTest.class));
		assertEquals(100, TypeUtil.computeDistance(I0Test.class, I1Test.class));
		assertEquals(100, TypeUtil.computeDistance(I0Test.class, VTest.class));
		assertEquals(200, TypeUtil.computeDistance(I0Test.class, WTest.class));
		assertEquals(100, TypeUtil.computeDistance(I1Test.class, WTest.class));
		assertEquals(100, TypeUtil.computeDistance(I0Test.class, XTest.class));
		assertEquals(200, TypeUtil.computeDistance(I0Test.class, YTest.class));
		assertEquals(300, TypeUtil.computeDistance(J0Test.class, YTest.class));
		assertEquals(400, TypeUtil.computeDistance(I0Test.class, ZTest.class));
	}

	@Test
	public void testIsInstance() {
		Object object = new ZTest();
		assertTrue(TypeUtil.isInstanceOf(I0Test.class, object));
		assertTrue(TypeUtil.isInstanceOf("py4j.reflection.I0Test", object));
		object = new ATest();
		assertFalse(TypeUtil.isInstanceOf(I0Test.class, object));
		assertFalse(TypeUtil.isInstanceOf("py4j.reflection.I0Test", object));
	}
}

class ATest {

}

class BTest extends ATest {

}

class CTest extends BTest {

}

class DTest extends CTest {

}

interface I0Test {

}

interface I1Test extends I0Test {

}

interface I2Test extends I1Test {

}

interface I3Test extends I2Test {

}

interface J0Test {

}

class VTest implements I0Test, J0Test {

}

class WTest extends VTest implements I1Test {

}

class XTest extends VTest implements I0Test {

}

class YTest extends XTest implements I2Test {

}

class ZTest implements I3Test {

}
