<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:workflow="uri:oozie:workflow:0.5" exclude-result-prefixes="workflow">

<xsl:include href="0.1/workflow.xslt"/>
<xsl:include href="0.2/workflow.xslt"/>
<xsl:include href="0.2.5/workflow.xslt"/>
<xsl:include href="0.3/workflow.xslt"/>
<xsl:include href="0.4/workflow.xslt"/>
<xsl:include href="0.5/workflow.xslt"/>

<xsl:template match="/">

    <xsl:apply-templates select="*"/>

</xsl:template>

<xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes"/>
</xsl:stylesheet>