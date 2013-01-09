<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:workflow="uri:oozie:workflow:0.1" exclude-result-prefixes="workflow">

<xsl:import href="extensions/distcp.0.1.xslt"/>
<xsl:import href="extensions/email.0.1.xslt"/>
<xsl:import href="extensions/hive.0.1.xslt"/>
<xsl:import href="extensions/hive.0.2.xslt"/>
<xsl:import href="extensions/shell.0.1.xslt"/>
<xsl:import href="extensions/sqoop.0.1.xslt"/>
<xsl:import href="extensions/sqoop.0.2.xslt"/>
<xsl:import href="nodes/fs.xslt"/>
<xsl:import href="nodes/java.xslt"/>
<xsl:import href="nodes/mapreduce.xslt"/>
<xsl:import href="nodes/pig.xslt"/>
<xsl:import href="nodes/streaming.xslt"/>
<xsl:import href="nodes/generic.xslt"/>
<xsl:import href="nodes/ssh.xslt"/>
<xsl:import href="nodes/subworkflow.xslt"/>

<xsl:template match="workflow:action" xmlns:workflow="uri:oozie:workflow:0.1">

  <object model="oozie.node" pk="0">

    <field name="name" type="CharField">
      <xsl:value-of select="@name"/>
    </field>
    <field name="node_type" type="CharField">
      <xsl:value-of select="name(*)"/>
    </field>

  </object>

  <xsl:apply-templates select="*"/>

</xsl:template>

<xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes"/>
</xsl:stylesheet>