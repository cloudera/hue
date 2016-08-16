<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:template name="deletes">

  "deletes": [

    <xsl:for-each select="*[local-name()='delete']">
      {"value": "<xsl:value-of select="@path"/>"}
      <xsl:if  test="position() &lt; last()">
        ,
      </xsl:if>
    </xsl:for-each>
  ]
</xsl:template>

</xsl:stylesheet>