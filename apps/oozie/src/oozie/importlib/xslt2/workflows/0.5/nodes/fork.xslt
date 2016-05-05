<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:workflow5="uri:oozie:workflow:0.5" xmlns:workflow4="uri:oozie:workflow:0.4">

<xsl:template match="workflow5:fork | workflow4:fork" xmlns:workflow5="uri:oozie:workflow:0.5" xmlns:workflow4="uri:oozie:workflow:0.4">
  <xsl:for-each select="*">
    ,"path<xsl:value-of select='position()'/>": "<xsl:value-of select="@start"/>"
  </xsl:for-each>
</xsl:template>

</xsl:stylesheet>