<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:workflow="uri:oozie:workflow:0.5" xmlns:distcp="uri:oozie:distcp-action:0.2" exclude-result-prefixes="workflow distcp">

<xsl:template match="distcp:distcp">

  ,"params": [
        <xsl:for-each select="*[local-name()='arg']">
          <xsl:choose>
            <xsl:when test="position() &lt; last()">
              {"type":"arg","value":"<xsl:value-of select="."/>"},
            </xsl:when>
            <xsl:otherwise>
              {"type":"arg","value":"<xsl:value-of select="."/>"}
            </xsl:otherwise>
          </xsl:choose>
        </xsl:for-each>
    ]

</xsl:template>

</xsl:stylesheet>