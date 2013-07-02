<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:workflow="uri:oozie:workflow:0.1" xmlns:shell="uri:oozie:shell-action:0.1" exclude-result-prefixes="workflow shell">

<xsl:import href="../nodes/fields/archives.xslt"/>
<xsl:import href="../nodes/fields/capture_output.xslt"/>
<xsl:import href="../nodes/fields/command.xslt"/>
<xsl:import href="../nodes/fields/files.xslt"/>
<xsl:import href="../nodes/fields/job_properties.xslt"/>
<xsl:import href="../nodes/fields/job_xml.xslt"/>
<xsl:import href="../nodes/fields/arguments.xslt"/>
<xsl:import href="../nodes/fields/prepares.xslt"/>

<xsl:template match="shell:shell">

  <object model="oozie.shell" pk="0">

    <xsl:call-template name="archives"/>
    <xsl:call-template name="capture_output"/>
    <xsl:call-template name="command"/>
    <xsl:call-template name="files"/>
    <xsl:call-template name="job_properties"/>
    <xsl:call-template name="job_xml"/>
    <xsl:call-template name="arguments"/>
    <xsl:call-template name="prepares"/>

  </object>

</xsl:template>

<xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes"/>
</xsl:stylesheet>