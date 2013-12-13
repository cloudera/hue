<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:workflow="uri:oozie:workflow:0.5" exclude-result-prefixes="workflow">

<xsl:import href="fields/archives.xslt"/>
<xsl:import href="fields/files.xslt"/>
<xsl:import href="fields/jar_path.xslt"/>
<xsl:import href="fields/job_properties.xslt"/>
<xsl:import href="fields/job_xml.xslt"/>
<xsl:import href="fields/prepares.xslt"/>

<xsl:template match="workflow:map-reduce" xmlns:workflow="uri:oozie:workflow:0.5">

  <object model="oozie.mapreduce" pk="0">

    <xsl:call-template name="files"/>
    <xsl:call-template name="archives"/>
    <xsl:call-template name="jar_path"/>
    <xsl:call-template name="job_properties"/>
    <xsl:call-template name="job_xml"/>
    <xsl:call-template name="prepares"/>

  </object>

</xsl:template>

<xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes"/>
</xsl:stylesheet>