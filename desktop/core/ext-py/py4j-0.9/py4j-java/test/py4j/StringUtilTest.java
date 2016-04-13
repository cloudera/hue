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
package py4j;

import static org.junit.Assert.assertEquals;

import org.junit.Test;

public class StringUtilTest {

	@Test
	public void testEmptyString() {
		assertEquals("", StringUtil.unescape(""));
	}

	@Test
	public void testNoEscape() {
		assertEquals("Hello", StringUtil.unescape("Hello"));
		assertEquals("Hello World!", StringUtil.unescape("Hello World!"));
		assertEquals("Hello\tWorld!\"", StringUtil.unescape("Hello\tWorld!\""));
	}

	@Test
	public void testWithEscape() {
		assertEquals("Hello\\World!", StringUtil.unescape("Hello\\\\World!"));
		assertEquals("Hello \\\\World!",
				StringUtil.unescape("Hello \\\\\\\\World!"));
	}

	@Test
	public void testWithLineBreaks() {
		assertEquals("Hello\\nWorld!", StringUtil.unescape("Hello\\\\nWorld!"));
		assertEquals("Hello\nWorld!", StringUtil.unescape("Hello\\nWorld!"));
		assertEquals("Hello\\\nWorld!",
				StringUtil.unescape("Hello\\\\\\nWorld!"));
		assertEquals("\rHello\\\nWorld!",
				StringUtil.unescape("\\rHello\\\\\\nWorld!"));
	}

	@Test
	public void testEscape() {
		assertEquals("Hello\\\\nWorld!", StringUtil.escape("Hello\\nWorld!"));
		assertEquals("Hello\\nWorld!", StringUtil.escape("Hello\nWorld!"));
		assertEquals("\\r\tHello\\nWorld!",
				StringUtil.escape("\r\tHello\nWorld!"));
		assertEquals("Hello\\\\\\nWorld!", StringUtil.escape("Hello\\\nWorld!"));
		assertEquals("Hello\tWorld", StringUtil.escape("Hello\tWorld"));
		assertEquals("Hello\\\\World!", StringUtil.escape("Hello\\World!"));
	}

}
