<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:import href="nodes/decision.xslt"/>
<xsl:import href="nodes/end.xslt"/>
<xsl:import href="nodes/fork.xslt"/>
<xsl:import href="nodes/join.xslt"/>
<xsl:import href="nodes/kill.xslt"/>
<xsl:import href="nodes/start.xslt"/>

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