<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:template name="jar_path">

  <field name="jar_path" type="CharField">
    <xsl:value-of select="*[local-name()='jar-path']"/>
  </field>

</xsl:template>

<xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes"/>
</xsl:stylesheet>