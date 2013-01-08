<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:workflow="uri:oozie:workflow:0.4" exclude-result-prefixes="workflow">

<xsl:template name="job_properties">

  <field name="job_properties" type="TextField">
    <xsl:text>[</xsl:text>
    <xsl:for-each select="*[local-name()='configuration']/*[local-name()='property']">
      <xsl:choose>
        <xsl:when test="position() &lt; last()">
          <xsl:text><![CDATA[{"name":"]]></xsl:text><xsl:value-of select="*[local-name()='name']" /><xsl:text><![CDATA[","value":"]]></xsl:text><xsl:value-of select="*[local-name()='value']" /><xsl:text><![CDATA["},]]></xsl:text>
        </xsl:when>
        <xsl:otherwise>
          <xsl:text><![CDATA[{"name":"]]></xsl:text><xsl:value-of select="*[local-name()='name']" /><xsl:text><![CDATA[","value":"]]></xsl:text><xsl:value-of select="*[local-name() ='value']" /><xsl:text><![CDATA["}]]></xsl:text>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:for-each>
    <xsl:text>]</xsl:text>
  </field>

</xsl:template>

</xsl:stylesheet>