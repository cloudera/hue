<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:workflow="uri:oozie:workflow:0.4" exclude-result-prefixes="workflow">

<xsl:import href="fields/job_properties.xslt"/>
<xsl:import href="fields/propagate_configuration.xslt"/>

<xsl:template match="workflow:sub-workflow" xmlns:workflow="uri:oozie:workflow:0.4">

  <object model="oozie.subworkflow" pk="0">

    <xsl:call-template name="job_properties"/>
    <xsl:call-template name="propagate_configuration"/>

  </object>

</xsl:template>

<xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes"/>
</xsl:stylesheet>