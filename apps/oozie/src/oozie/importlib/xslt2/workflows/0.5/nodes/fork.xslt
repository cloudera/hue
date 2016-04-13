<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:workflow="uri:oozie:workflow:0.5" exclude-result-prefixes="workflow">

<xsl:template match="workflow:fork" xmlns:workflow="uri:oozie:workflow:0.5">
  <xsl:for-each select="*">
    ,"path<xsl:value-of select='position()'/>": "<xsl:value-of select="@start"/>"
  </xsl:for-each>
</xsl:template>

</xsl:stylesheet>