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

import org.junit.Test;

public class TypeConverterTest {

	@Test
	public void testTypeConversion() {
		TypeConverter converter = new TypeConverter();
		assertEquals("test", converter.convert("test"));
		assertTrue(converter.convert("test") instanceof String);
	}

	@Test
	public void testDoubleConversion() {
		TypeConverter converter = new TypeConverter(
				TypeConverter.DOUBLE_TO_FLOAT);
		assertEquals(1.2f, converter.convert(1.2));
		assertTrue(converter.convert(1.2) instanceof Float);
	}

	@Test
	public void testIntConversion() {
		TypeConverter converter = new TypeConverter(TypeConverter.INT_TO_SHORT);
		assertEquals((short) 100, converter.convert(100));
		assertTrue(converter.convert(100) instanceof Short);

		converter = new TypeConverter(TypeConverter.INT_TO_BYTE);
		assertEquals((byte) 100, converter.convert(100));
		assertTrue(converter.convert(102) instanceof Byte);
	}

	@Test
	public void testStringConversion() {
		TypeConverter converter = new TypeConverter(
				TypeConverter.STRING_TO_CHAR);
		assertEquals('c', converter.convert("c"));
		assertTrue(converter.convert("c") instanceof Character);
	}
}
