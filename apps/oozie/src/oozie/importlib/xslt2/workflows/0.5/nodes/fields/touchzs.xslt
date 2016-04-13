<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:workflow="uri:oozie:workflow:0.5" exclude-result-prefixes="workflow">

<xsl:template name="touchzs">

  "touchzs": {

    <xsl:for-each select="*[local-name()='touchz']">
      "path<xsl:value-of select='position()'/>": "<xsl:value-of select="@path"/>"
      <xsl:if  test="position() &lt; last()">
        ,
      </xsl:if>
    </xsl:for-each>
  }
</xsl:template>

</xsl:stylesheet>