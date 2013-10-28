<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:workflow="uri:oozie:workflow:0.3" exclude-result-prefixes="workflow">

<xsl:template name="chmods">

  <field name="chmods" type="TextField">

    <xsl:text>[</xsl:text>
    <xsl:for-each select="*[local-name()='chmod']">
      <xsl:choose>
        <xsl:when test="position() &lt; last()">
          <xsl:text><![CDATA[{"path":"]]></xsl:text>
          <xsl:value-of select="@path" />
          <xsl:text><![CDATA[","permissions":"]]></xsl:text>
          <xsl:value-of select="@permissions" />
          <xsl:text><![CDATA[","recursive":"]]></xsl:text>
          <xsl:value-of select="@dir-files" />
          <xsl:text><![CDATA["},]]></xsl:text>
        </xsl:when>
        <xsl:otherwise>
          <xsl:text><![CDATA[{"path":"]]></xsl:text>
          <xsl:value-of select="@path" />
          <xsl:text><![CDATA[","permissions":"]]></xsl:text>
          <xsl:value-of select="@permissions" />
          <xsl:text><![CDATA[","recursive":"]]></xsl:text>
          <xsl:value-of select="@dir-files" />
          <xsl:text><![CDATA["}]]></xsl:text>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:for-each>
    <xsl:text>]</xsl:text>

  </field>

</xsl:template>

<xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes"/>
</xsl:stylesheet>