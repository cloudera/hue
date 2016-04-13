Build with:

```
% mvn package
% virtualenv build
% ./build/bin/pip install py4j
```

Start JVM:

```
% java -jar target/dbproxy-1.0-SNAPSHOT.jar
```

Run a query:

```
% ./build/bin/python query.py
```
