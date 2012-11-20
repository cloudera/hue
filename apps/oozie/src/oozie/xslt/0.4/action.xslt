<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:import href="extensions/distcp.0.1.xslt"/>
<xsl:import href="extensions/hive.0.1.xslt"/>
<xsl:import href="extensions/hive.0.2.xslt"/>
<xsl:import href="extensions/shell.0.1.xslt"/>
<xsl:import href="extensions/sqoop.0.1.xslt"/>
<xsl:import href="extensions/sqoop.0.2.xslt"/>
<xsl:import href="extensions/ssh.0.1.xslt"/>
<xsl:import href="nodes/java.xslt"/>
<xsl:import href="nodes/mapreduce.xslt"/>
<xsl:import href="nodes/pig.xslt"/>
<xsl:import href="nodes/streaming.xslt"/>

<xsl:template match="action">

  <object model="oozie.node" pk="0">

    <field name="name" type="CharField">
      <xsl:value-of select="@name"/>
    </field>
    <field name="node_type" type="CharField">
      <xsl:value-of select="name(.)"/>
    </field>

  </object>

  <xsl:apply-templates select="*"/>

</xsl:template>

<xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes"/>
</xsl:stylesheet>