<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:coordinator="uri:oozie:coordinator:0.1" exclude-result-prefixes="coordinator">

<xsl:template match="coordinator:dataset" xmlns:coordinator="uri:oozie:coordinator:0.1">

  <object model="oozie.dataset" pk="0">

    <field name="name" type="CharField">
      <xsl:value-of select="@name"/>
    </field>
    <field name="timezone" type="CharField">
      <xsl:value-of select="@timezone"/>
    </field>
    <field name="uri" type="CharField">
      <xsl:value-of select="coordinator:uri-template"/>
    </field>
    <field name="done_flag" type="CharField">
      <xsl:value-of select="coordinator:done-flag"/>
    </field>

  </object>

</xsl:template>

<xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes"/>
</xsl:stylesheet>
