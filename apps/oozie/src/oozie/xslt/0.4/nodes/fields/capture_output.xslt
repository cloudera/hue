<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:template name="capture_output">

  <field name="capture_output" type="BooleanField">
    <xsl:choose>
      <xsl:when test="*[local-name()='exec']">
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