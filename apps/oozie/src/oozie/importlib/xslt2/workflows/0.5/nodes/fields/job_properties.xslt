<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:workflow="uri:oozie:workflow:0.5" exclude-result-prefixes="workflow">

<xsl:template name="job_properties">
  ,"job_properties": [
    <xsl:for-each select="*[local-name()='configuration']/*[local-name()='property']">
      <xsl:choose>
        <xsl:when test="position() &lt; last()">
          {"name": "<xsl:value-of select="*[local-name()='name']" />", "value": "<xsl:value-of select="*[local-name()='value']" />"},
        </xsl:when>
        <xsl:otherwise>
          {"name": "<xsl:value-of select="*[local-name()='name']" />", "value": "<xsl:value-of select="*[local-name()='value']" />"}
        </xsl:otherwise>
      </xsl:choose>
    </xsl:for-each>
    ]
</xsl:template>

</xsl:stylesheet>