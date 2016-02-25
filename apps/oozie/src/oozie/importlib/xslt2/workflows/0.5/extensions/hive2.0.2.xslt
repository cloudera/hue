<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:workflow="uri:oozie:workflow:0.5" xmlns:hive2="uri:oozie:hive2-action:0.2" exclude-result-prefixes="workflow hive">

<xsl:template match="hive2:hive2">

  ,"hive": {"script": "<xsl:value-of select="*[local-name()='script']"/>"}

</xsl:template>

</xsl:stylesheet>