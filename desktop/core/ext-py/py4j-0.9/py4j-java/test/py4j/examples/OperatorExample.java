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
package py4j.examples;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;

import py4j.GatewayServer;

public class OperatorExample {

	private final static int MAX = 1000;

    public OperatorExample() {

    }

    public OperatorExample(Operator op) {
        this.randomBinaryOperator(op);
    }

	public byte[] callBytesOperator(BytesOperator op) {
		byte[] input = { 1, 2, 3, 4, 5 };

		return op.returnBytes(input);
	}

	public List<Integer> randomBinaryOperator(Operator op) {
		Random random = new Random();
		List<Integer> numbers = new ArrayList<Integer>();
		numbers.add(random.nextInt(MAX));
		numbers.add(random.nextInt(MAX));
		numbers.add(op.doOperation(numbers.get(0), numbers.get(1)));
		return numbers;
	}

	public List<Integer> randomTernaryOperator(Operator op) {
		Random random = new Random();
		List<Integer> numbers = new ArrayList<Integer>();
		numbers.add(random.nextInt(MAX));
		numbers.add(random.nextInt(MAX));
		numbers.add(random.nextInt(MAX));
		numbers.add(op.doOperation(numbers.get(0), numbers.get(1),
				numbers.get(2)));
		return numbers;
	}

	public static void main(String[] args) {
		GatewayServer server = new GatewayServer(new OperatorExample());
		server.start();
	}

}
