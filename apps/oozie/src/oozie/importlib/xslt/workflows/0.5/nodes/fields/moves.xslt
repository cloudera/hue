<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:workflow="uri:oozie:workflow:0.5" exclude-result-prefixes="workflow">

<xsl:template name="moves">

  <field name="moves" type="TextField">

    <xsl:text>[</xsl:text>
    <xsl:for-each select="*[local-name()='move']">
      <xsl:choose>
        <xsl:when test="position() &lt; last()">
          <xsl:text><![CDATA[{"source":"]]></xsl:text>
          <xsl:value-of select="@source" />
          <xsl:text><![CDATA[","destination":"]]></xsl:text>
          <xsl:value-of select="@target" />
          <xsl:text><![CDATA["},]]></xsl:text>
        </xsl:when>
        <xsl:otherwise>
          <xsl:text><![CDATA[{"source":"]]></xsl:text>
          <xsl:value-of select="@source" />
          <xsl:text><![CDATA[","destination":"]]></xsl:text>
          <xsl:value-of select="@target" />
          <xsl:text><![CDATA["}]]></xsl:text>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:for-each>
    <xsl:text>]</xsl:text>

  </field>

</xsl:template>

<xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes"/>
</xsl:stylesheet>