<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:workflow="uri:oozie:workflow:0.5" xmlns:distcp="uri:oozie:distcp-action:0.1" exclude-result-prefixes="workflow distcp">

<xsl:import href="../nodes/fields/job_xml.xslt"/>

<xsl:template match="distcp:distcp">

  ,"distcp": <xsl:call-template name="job_xml"/>

</xsl:template>

</xsl:stylesheet>