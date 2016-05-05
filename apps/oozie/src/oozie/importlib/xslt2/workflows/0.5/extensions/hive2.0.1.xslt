<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:hive2="uri:oozie:hive2-action:0.1">

<xsl:template match="hive2:hive2">

  ,"hive": {"script": "<xsl:value-of select="*[local-name()='script']"/>"}

</xsl:template>

</xsl:stylesheet>