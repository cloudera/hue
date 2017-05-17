<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:workflow5="uri:oozie:workflow:0.5" xmlns:workflow4="uri:oozie:workflow:0.4" xmlns:workflow3="uri:oozie:workflow:0.3" xmlns:workflow2="uri:oozie:workflow:0.2" xmlns:workflow1="uri:oozie:workflow:0.1">

<xsl:include href="action.xslt"/>
<xsl:include href="control.xslt"/>

<xsl:template match="/workflow5:workflow-app">

   [ <xsl:apply-templates select="workflow5:start | workflow5:end | workflow5:decision | workflow5:fork | workflow5:join | workflow5:kill"/>
    <xsl:apply-templates select="workflow5:action"/> {}]

</xsl:template>

<xsl:template match="/workflow4:workflow-app">

   [ <xsl:apply-templates select="workflow4:start | workflow4:end | workflow4:decision | workflow4:fork | workflow4:join | workflow4:kill"/>
    <xsl:apply-templates select="workflow4:action"/> {}]

</xsl:template>

<xsl:template match="/workflow3:workflow-app">

   [ <xsl:apply-templates select="workflow3:start | workflow3:end | workflow3:decision | workflow3:fork | workflow3:join | workflow3:kill"/>
    <xsl:apply-templates select="workflow3:action"/> {}]

</xsl:template>

<xsl:template match="/workflow2:workflow-app">

   [ <xsl:apply-templates select="workflow2:start | workflow2:end | workflow2:decision | workflow2:fork | workflow2:join | workflow2:kill"/>
    <xsl:apply-templates select="workflow2:action"/> {}]

</xsl:template>

<xsl:template match="/workflow1:workflow-app">

   [ <xsl:apply-templates select="workflow1:start | workflow1:end | workflow1:decision | workflow1:fork | workflow1:join | workflow1:kill"/>
    <xsl:apply-templates select="workflow1:action"/> {}]

</xsl:template>


<xsl:output method="text" indent="no" omit-xml-declaration="yes"/>
</xsl:stylesheet>