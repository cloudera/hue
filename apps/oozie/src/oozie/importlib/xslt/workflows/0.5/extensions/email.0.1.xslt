<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:workflow="uri:oozie:workflow:0.5" xmlns:email="uri:oozie:email-action:0.1" exclude-result-prefixes="workflow email">

<xsl:template match="email:email">

  <object model="oozie.email" pk="0">

    <field name="to" type="CharField">
      <xsl:value-of select="*[local-name()='to']"/>
    </field>

    <field name="cc" type="CharField">
      <xsl:value-of select="*[local-name()='cc']"/>
    </field>

    <field name="subject" type="CharField">
      <xsl:value-of select="*[local-name()='subject']"/>
    </field>

    <field name="body" type="CharField">
      <xsl:value-of select="*[local-name()='body']"/>
    </field>

  </object>

</xsl:template>

<xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes"/>
</xsl:stylesheet>