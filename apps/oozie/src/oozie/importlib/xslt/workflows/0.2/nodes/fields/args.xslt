<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:workflow="uri:oozie:workflow:0.2" exclude-result-prefixes="workflow">

<xsl:template name="args">

  <field name="args" type="CharField">
    <xsl:for-each select="*[local-name()='arg']">
      <xsl:value-of select="." />
      <xsl:if  test="position() &lt; last()">
        <xsl:text> </xsl:text>
      </xsl:if>
    </xsl:for-each>
  </field>

</xsl:template>

</xsl:stylesheet>