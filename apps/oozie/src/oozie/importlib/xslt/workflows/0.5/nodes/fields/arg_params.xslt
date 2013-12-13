<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:workflow="uri:oozie:workflow:0.5" exclude-result-prefixes="workflow">

<xsl:template name="arg_params">

  <field name="params" type="TextField">
    <xsl:text>[</xsl:text>
    <xsl:for-each select="*[local-name()='arg']">
      <xsl:choose>
        <xsl:when test="position() &lt; last()">
          <xsl:text><![CDATA[{"type":"arg","value":"]]></xsl:text><xsl:value-of select="." /><xsl:text><![CDATA["},]]></xsl:text>
        </xsl:when>
        <xsl:otherwise>
          <xsl:text><![CDATA[{"type":"arg","value":"]]></xsl:text><xsl:value-of select="." /><xsl:text><![CDATA["}]]></xsl:text>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:for-each>
    <xsl:text>]</xsl:text>
  </field>

</xsl:template>

</xsl:stylesheet>