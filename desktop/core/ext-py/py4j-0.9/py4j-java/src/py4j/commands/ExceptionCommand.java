package py4j.commands;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.util.logging.Logger;

import py4j.Protocol;
import py4j.Py4JException;
import py4j.ReturnObject;

public class ExceptionCommand extends AbstractCommand {

	private final Logger logger = Logger.getLogger(ExceptionCommand.class
			.getName());

	public final static String EXCEPTION_COMMAND_NAME = "p";

	public ExceptionCommand() {
		super();
		this.commandName = EXCEPTION_COMMAND_NAME;
	}

	@Override
	public void execute(String commandName, BufferedReader reader,
			BufferedWriter writer) throws Py4JException, IOException {
		String returnCommand = null;
		Throwable exception = (Throwable) Protocol.getObject(reader.readLine(),
				this.gateway);
		// EOQ
		reader.readLine();

		String stackTrace = Protocol.getThrowableAsString(exception);
		ReturnObject rObject = ReturnObject
				.getPrimitiveReturnObject(stackTrace);
		returnCommand = Protocol.getOutputCommand(rObject);

		logger.finest("Returning command: " + returnCommand);
		writer.write(returnCommand);
		writer.flush();
	}

}
