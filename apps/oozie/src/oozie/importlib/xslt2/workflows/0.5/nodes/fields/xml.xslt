<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">


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

  "xml":
    <xsl:text disable-output-escaping="yes">"&lt;![CDATA[</xsl:text>,
    <xsl:apply-templates  select="current()" mode="copy-no-namespaces"/>
    <xsl:text disable-output-escaping="yes">]]&gt;"</xsl:text>,

</xsl:template>

</xsl:stylesheet>