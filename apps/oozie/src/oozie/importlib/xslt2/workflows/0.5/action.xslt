<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:workflow="uri:oozie:workflow:0.5" exclude-result-prefixes="workflow">

<xsl:import href="extensions/distcp.0.1.xslt"/>
<xsl:import href="extensions/email.0.1.xslt"/>
<xsl:import href="extensions/hive.0.1.xslt"/>
<xsl:import href="extensions/hive.0.2.xslt"/>
<xsl:import href="extensions/shell.0.1.xslt"/>
<xsl:import href="extensions/sqoop.0.1.xslt"/>
<xsl:import href="extensions/sqoop.0.2.xslt"/>
<xsl:import href="extensions/ssh.0.1.xslt"/>
<xsl:import href="nodes/fs.xslt"/>
<xsl:import href="nodes/java.xslt"/>
<xsl:import href="nodes/mapreduce.xslt"/>
<xsl:import href="nodes/pig.xslt"/>
<xsl:import href="nodes/streaming.xslt"/>
<xsl:import href="nodes/generic.xslt"/>
<xsl:import href="nodes/subworkflow.xslt"/>

<xsl:template match="workflow:action" xmlns:workflow="uri:oozie:workflow:0.5">
  {
    "name": "<xsl:value-of select="@name"/>",
    "node_type": "<xsl:value-of select="name(*)"/>",

    <xsl:variable name="ok" select="'ok'"/>
    <xsl:variable name="error" select="'error'"/>
    "ok_to": "<xsl:value-of select="*[name()=$ok]/@to"/>",
    "error_to": "<xsl:value-of select="*[name()=$error]/@to"/>"

    <xsl:apply-templates select="*"/>
  },
</xsl:template>

</xsl:stylesheet>