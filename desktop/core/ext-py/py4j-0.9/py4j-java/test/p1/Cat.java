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
package p1;

import p1.p2.Animal;

public class Cat extends Animal {

	public int age2 = 2;

	public static final String CONSTANT = "Salut!";

	@SuppressWarnings("unused")
	private String age3 = "";

	double age4 = 2.2;

	protected char age5 = 'a';

	public static StringBuffer myBuffer = new StringBuffer("Hello");

	public Cat() {

	}

	public Cat(int i) {

	}

	public Cat(String s1, String s2) {

	}

	public Cat(char c1, int i2) {

	}

	public Cat(boolean b1, short s1) {

	}

	public Cat(Object obj, String s2) {

	}

	public static void meowmeow(String s) {
		System.out.println("meowmoewcat");
	}

	public void meow(long s) {
		System.out.println("meowlongcat");
	}

	public void meow(boolean s) {
		System.out.println("meowboolcat");
	}

	public void meow(Object o) {
		System.out.println("meowobjectcat");
	}

	@SuppressWarnings("unused")
	private void meow2(Cat cat) {
		System.out.println("meowcatcat");
	}

	protected void meow3(Cat cat) {
		System.out.println("meowcatcat");
	}

	void meow4(Cat cat) {
		System.out.println("meowcatcat");
	}

	public void meow5(String s1, String s2) {
		System.out.println("Meowing: " + s1 + s2);
	}

	public void meow10(float f) {
		System.out.println("Meowing float " + f);
	}

	public void meow11() {
		System.out.println("Meowing");
	}

	public int meow12() {
		return 1;
	}

	public int meow13(long p1, int p2, short p3, byte p4, double p5, Float p6,
			boolean p7, String p8, char p9) {
		return 10;
	}

	public int meow14(Long p1, int p2, short p3, byte p4, double p5, Float p6,
			boolean p7, String p8, char p9) {
		return 10;
	}

	public static void meow15() {

	}

	public class SmallCat {
		public int age = 2;

		public void method1() {

		}
	}

}
