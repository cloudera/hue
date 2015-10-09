from py4j.java_gateway import JavaGateway

gateway = JavaGateway()

jdbc_driver = 'com.mysql.jdb.Driver'
db_url = 'jdbc:mysql://localhost/hue'
username = 'root'
password = 'root'

conn = gateway.jvm.java.sql.DriverManager.getConnection(db_url, username, password)

try:
  stmt = conn.createStatement()
  try:
    rs = stmt.executeQuery('select username,email from auth_user')

    try:

      md = rs.getMetaData()

      for i in xrange(md.getColumnCount()):
         print md.getColumnTypeName(i + 1)

      while rs.next():
        username = rs.getString("username")
        email = rs.getString("email")
        print username, email
    finally:
      rs.close()
  finally:
    stmt.close()
finally:
  conn.close()
