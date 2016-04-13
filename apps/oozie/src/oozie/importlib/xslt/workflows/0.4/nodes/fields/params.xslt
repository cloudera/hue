<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:workflow="uri:oozie:workflow:0.4" exclude-result-prefixes="workflow">

<xsl:template name="params">

  <field name="params" type="TextField">
    <xsl:text>[</xsl:text>
    <xsl:for-each select="*[local-name()='param'] | *[starts-with(local-name(), 'arg')]">
      <xsl:choose>
        <xsl:when test="position() &lt; last()">
          <xsl:text><![CDATA[{"type":"]]></xsl:text><xsl:value-of select="local-name()" /><xsl:text><![CDATA[","value":"]]></xsl:text><xsl:value-of select="." /><xsl:text><![CDATA["},]]></xsl:text>
        </xsl:when>
        <xsl:otherwise>
          <xsl:text><![CDATA[{"type":"]]></xsl:text><xsl:value-of select="local-name()" /><xsl:text><![CDATA[","value":"]]></xsl:text><xsl:value-of select="." /><xsl:text><![CDATA["}]]></xsl:text>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:for-each>
    <xsl:text>]</xsl:text>
  </field>

</xsl:template>

</xsl:stylesheet>
