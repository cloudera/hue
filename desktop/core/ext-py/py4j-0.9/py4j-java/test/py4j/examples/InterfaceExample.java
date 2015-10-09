package py4j.examples;

import py4j.GatewayServer;

public class InterfaceExample {

	public void test(InterfaceB b) {
		InterfaceA a = b.getA();
		System.out.println(a.getClass().getName());
	}

	public static void main(String[] args) {
		GatewayServer server = new GatewayServer(new InterfaceExample());
		server.start();
	}
}
