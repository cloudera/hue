Py4J Java API
=============

The Java API is under active development and will be refactored in the next releases. You can browse the `javadoc <_static/javadoc/index.html>`_, but most classes are not documented yet.

For now, the best way to use the API is to:

1. Create a class that extends the `DefaultGateway <_static/javadoc/index.html?py4j/DefaultGateway.html>`_.
2. Initialize a `GatewayServer <_static/javadoc/index.html?py4j/GatewayServer.html>`_ with your newly created class.
3. Call the `Gateway.start() <_static/javadoc/py4j/GatewayServer.html#start(boolean)>`_ method to enable your Python program to access your gateway.