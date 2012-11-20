<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:template name="args">

  <field name="args" type="CharField">
    <xsl:text>[</xsl:text>
    <xsl:for-each select="*[local-name()='arg']">
      <xsl:text><![CDATA["]]></xsl:text><xsl:value-of select="." /><xsl:text><![CDATA["]]></xsl:text>
      <xsl:if  test="position() &lt; last()">
        <xsl:text>,</xsl:text>
      </xsl:if>
    </xsl:for-each>
    <xsl:text>]</xsl:text>
  </field>

</xsl:template>

</xsl:stylesheet>