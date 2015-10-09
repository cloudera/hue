package py4j.examples;

import py4j.GatewayServer;

public class TestNoneApplication {

	public String testNone(InterfaceNone iNone) {
		String s = iNone.getName();
		
		return s;
	}
	
	/**
	 * @param args
	 */
	public static void main(String[] args) {
		GatewayServer server = new GatewayServer(new TestNoneApplication());
		server.start();
	}

}
