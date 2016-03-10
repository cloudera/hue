package py4j.commands;

import static org.junit.Assert.assertTrue;
import static org.junit.Assert.fail;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.StringReader;
import java.io.StringWriter;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;

import py4j.Gateway;

public class ExceptionCommandTest {
	private Gateway gateway;
	private ExceptionCommand command;
	private BufferedWriter writer;
	private StringWriter sWriter;

	@Before
	public void setUp() {
		gateway = new Gateway(null);
		gateway.startup();
		command = new ExceptionCommand();
		command.init(gateway);
		sWriter = new StringWriter();
		writer = new BufferedWriter(sWriter);
	}

	@After
	public void tearDown() {
		gateway.shutdown();
	}

	@Test
	public void testException() {
		String id = null;
		try {
			throw new RuntimeException("Hello World");
		} catch (Exception e) {
			id = "r" + gateway.putNewObject(e);
		}

		String inputCommand = id + "\ne\n";
		try {
			command.execute("p", new BufferedReader(new StringReader(
					inputCommand)), writer);
			System.out.println("DEBUG!!!" + sWriter.toString());
			assertTrue(sWriter.toString().startsWith(
					"ysjava.lang.RuntimeException: Hello World\\n"));
		} catch (Exception e) {
			e.printStackTrace();
			fail();
		}
	}
}
