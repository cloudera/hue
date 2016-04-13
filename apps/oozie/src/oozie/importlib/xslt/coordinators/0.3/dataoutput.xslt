<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:coordinator="uri:oozie:coordinator:0.3" exclude-result-prefixes="coordinator">

<xsl:template match="coordinator:data-out" xmlns:coordinator="uri:oozie:coordinator:0.3">

  <object model="oozie.dataoutput" pk="0">

    <field name="name" type="CharField">
      <xsl:value-of select="@name"/>
    </field>

  </object>

</xsl:template>

<xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes"/>
</xsl:stylesheet>