<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:workflow="uri:oozie:workflow:0.3" exclude-result-prefixes="workflow">


<xsl:template match="*" mode="copy-no-namespaces">
    <xsl:element name="{local-name()}">
        <xsl:copy-of select="@*"/>
        <xsl:apply-templates select="node()" mode="copy-no-namespaces"/>
    </xsl:element>
</xsl:template>

<xsl:template match="comment()| processing-instruction()" mode="copy-no-namespaces">
    <xsl:copy/>
</xsl:template>

<xsl:template name="xml">

  <field name="xml" type="TextField">
    <xsl:text disable-output-escaping="yes">&lt;![CDATA[</xsl:text>
    <xsl:apply-templates  select="current()" mode="copy-no-namespaces"/>
    <xsl:text disable-output-escaping="yes">]]&gt;</xsl:text>
  </field>

</xsl:template>

<xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes"/>
</xsl:stylesheet>