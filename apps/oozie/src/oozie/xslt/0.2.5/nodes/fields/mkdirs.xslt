<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:workflow="uri:oozie:workflow:0.2.5" exclude-result-prefixes="workflow">

<xsl:template name="mkdirs">

  <field name="mkdirs" type="TextField">

    <xsl:text>[</xsl:text>
    <xsl:for-each select="*[local-name()='mkdir']">
      <xsl:text><![CDATA[{"name":"]]></xsl:text><xsl:value-of select="@path" /><xsl:text><![CDATA["}]]></xsl:text>
      <xsl:if  test="position() &lt; last()">
        <xsl:text>,</xsl:text>
      </xsl:if>
    </xsl:for-each>
    <xsl:text>]</xsl:text>

  </field>

</xsl:template>

<xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes"/>
</xsl:stylesheet>