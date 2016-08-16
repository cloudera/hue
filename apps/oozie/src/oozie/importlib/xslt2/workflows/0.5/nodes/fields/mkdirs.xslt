<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:template name="mkdirs">

  "mkdirs": [

    <xsl:for-each select="*[local-name()='mkdir']">
      {"value": "<xsl:value-of select="@path"/>"}
      <xsl:if  test="position() &lt; last()">
        ,
      </xsl:if>
    </xsl:for-each>
  ]
</xsl:template>

</xsl:stylesheet>