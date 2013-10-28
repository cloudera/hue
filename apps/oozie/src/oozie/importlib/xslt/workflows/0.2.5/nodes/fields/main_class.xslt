<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:workflow="uri:oozie:workflow:0.2.5" exclude-result-prefixes="workflow">

<xsl:template name="main_class">

  <field name="main_class" type="CharField">
    <xsl:value-of select="*[local-name()='main-class']"/>
  </field>

</xsl:template>

<xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes"/>
</xsl:stylesheet>