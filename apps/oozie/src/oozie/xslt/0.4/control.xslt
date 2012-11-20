<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:import href="decision.xslt"/>
<xsl:import href="end.xslt"/>
<xsl:import href="fork.xslt"/>
<xsl:import href="join.xslt"/>
<xsl:import href="kill.xslt"/>
<xsl:import href="start.xslt"/>

<xsl:template match="start | end | decision | fork | join | kill">

  <object model="oozie.node" pk="0">

    <field name="name" type="CharField">
      <xsl:value-of select="@name"/>
    </field>
    <field name="node_type" type="CharField">
      <xsl:value-of select="name(.)"/>
    </field>

  </object>

  <xsl:apply-imports/>

</xsl:template>

<xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes"/>
</xsl:stylesheet>