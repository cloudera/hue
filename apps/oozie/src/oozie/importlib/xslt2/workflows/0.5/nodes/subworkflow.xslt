<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:workflow="uri:oozie:workflow:0.5" exclude-result-prefixes="workflow">

<xsl:import href="fields/job_properties.xslt"/>

<xsl:template match="workflow:sub-workflow" xmlns:workflow="uri:oozie:workflow:0.5">
  , <xsl:call-template name="job_properties"/>
</xsl:template>

</xsl:stylesheet>