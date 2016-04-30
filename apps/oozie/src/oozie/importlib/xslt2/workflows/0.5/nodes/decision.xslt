<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:workflow="uri:oozie:workflow:0.5" exclude-result-prefixes="workflow">

<xsl:template match="workflow:decision" xmlns:workflow="uri:oozie:workflow:0.5">

  <xsl:for-each select="*[local-name()='switch']/*[local-name()='case']">
    ,"path<xsl:value-of select='position()'/>": "<xsl:value-of select='@to'/>"
  </xsl:for-each>
    ,"default": "<xsl:value-of select="*[local-name()='switch']/*[local-name()='default']/@to"/>"

</xsl:template>

<xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes"/>
</xsl:stylesheet>