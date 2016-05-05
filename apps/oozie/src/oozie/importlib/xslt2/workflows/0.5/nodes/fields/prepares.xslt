<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:template name="prepares">

  "prepares":

    <xsl:text>[</xsl:text>
    <xsl:for-each select="*[local-name()='prepare']/*">
      <xsl:choose>
        <xsl:when test="position() &lt; last()">
          <xsl:text><![CDATA[{"type":"]]></xsl:text><xsl:value-of select="local-name()" /><xsl:text><![CDATA[","value":"]]></xsl:text><xsl:value-of select="@path" /><xsl:text><![CDATA["},]]></xsl:text>
        </xsl:when>
        <xsl:otherwise>
          <xsl:text><![CDATA[{"type":"]]></xsl:text><xsl:value-of select="local-name()" /><xsl:text><![CDATA[","value":"]]></xsl:text><xsl:value-of select="@path" /><xsl:text><![CDATA["}]]></xsl:text>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:for-each>
    <xsl:text>]</xsl:text>

</xsl:template>

</xsl:stylesheet>
