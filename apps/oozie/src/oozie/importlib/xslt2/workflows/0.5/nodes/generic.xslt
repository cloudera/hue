<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">


<xsl:template match="*[name()!='decision' and name()!='end' and name()!='fork' and name()!='fs' and name()!='java' and name()!='join' and name()!='kill' and name()!='map-reduce' and name()!='pig' and name()!='start' and name()!='streaming' and name()!='sub-workflow' and name()!='distcp' and name()!='email' and name()!='hive' and name()!='hive2' and name()!='shell' and name()!='sqoop' and name()!='ssh' and name()!='ok' and name()!='error' and name()!='spark']">

</xsl:template>

</xsl:stylesheet>