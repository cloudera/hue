<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:workflow="uri:oozie:workflow:0.2.5" exclude-result-prefixes="workflow">

<xsl:include href="action.xslt"/>
<xsl:include href="control.xslt"/>

<xsl:template match="/workflow:workflow-app">

  <django-objects version="1.0">

    <xsl:apply-templates select="workflow:action"/>
    <xsl:apply-templates select="workflow:start | workflow:end | workflow:decision | workflow:fork | workflow:join | workflow:kill"/>

  </django-objects>

</xsl:template>

<xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes"/>
</xsl:stylesheet>