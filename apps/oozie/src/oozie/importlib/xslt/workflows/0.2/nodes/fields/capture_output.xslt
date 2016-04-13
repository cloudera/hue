<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:workflow="uri:oozie:workflow:0.4" exclude-result-prefixes="workflow">

<xsl:template name="capture_output">

  <field name="capture_output" type="BooleanField">
    <xsl:choose>
      <xsl:when test="*[local-name()='capture-output']">
        True
      </xsl:when>
      <xsl:otherwise>
        False
      </xsl:otherwise>
    </xsl:choose>
  </field>

</xsl:template>

<xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes"/>
</xsl:stylesheet>