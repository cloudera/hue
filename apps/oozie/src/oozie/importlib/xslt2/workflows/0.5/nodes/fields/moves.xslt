<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:template name="moves">

  "moves": [

    <xsl:for-each select="*[local-name()='move']">
      {"source": "<xsl:value-of select="@source"/>",
      "destination": "<xsl:value-of select="@target"/>"}
      <xsl:if  test="position() &lt; last()">
        ,
      </xsl:if>
    </xsl:for-each>
  ]
</xsl:template>

</xsl:stylesheet>