<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:workflow="uri:oozie:workflow:0.2" exclude-result-prefixes="workflow">

<xsl:template name="propagate_configuration">

  <field name="propagate_configuration" type="BooleanField">
    <xsl:choose>
      <xsl:when test="*[local-name()='propagate-configuration']">
        <xsl:text>True</xsl:text>
      </xsl:when>
      <xsl:otherwise>
        <xsl:text>False</xsl:text>
      </xsl:otherwise>
    </xsl:choose>
  </field>

</xsl:template>

<xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes"/>
</xsl:stylesheet>