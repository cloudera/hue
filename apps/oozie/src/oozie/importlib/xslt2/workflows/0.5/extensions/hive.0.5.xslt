<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:hive="uri:oozie:hive-action:0.5">

<xsl:template match="hive:hive">

  ,"hive": {"script": "<xsl:value-of select="*[local-name()='script']"/>"}

</xsl:template>

</xsl:stylesheet>