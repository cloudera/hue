<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:workflow="uri:oozie:workflow:0.2.5" exclude-result-prefixes="workflow">

<xsl:import href="fields/archives.xslt"/>
<xsl:import href="fields/files.xslt"/>
<xsl:import href="fields/job_properties.xslt"/>
<xsl:import href="fields/mapper.xslt"/>
<xsl:import href="fields/reducer.xslt"/>

<xsl:template match="workflow:streaming" xmlns:workflow="uri:oozie:workflow:0.2.5">

  <object model="oozie.streaming" pk="0">

    <xsl:call-template name="archives"/>
    <xsl:call-template name="files"/>
    <xsl:call-template name="job_properties"/>
    <xsl:call-template name="mapper"/>
    <xsl:call-template name="reducer"/>

  </object>

</xsl:template>

<xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes"/>
</xsl:stylesheet>