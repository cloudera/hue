<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:workflow="uri:oozie:workflow:0.5" xmlns:distcp="uri:oozie:distcp-action:0.1" exclude-result-prefixes="workflow distcp">

<xsl:template match="distcp:distcp">

  ,"distcp": {
        <xsl:for-each select="arg">
          "path<xsl:value-of select='position()'/>": "<xsl:value-of select="arg"/>"
          <xsl:if  test="position() &lt; last()">
            ,
          </xsl:if>
        </xsl:for-each>
    }

</xsl:template>

</xsl:stylesheet>