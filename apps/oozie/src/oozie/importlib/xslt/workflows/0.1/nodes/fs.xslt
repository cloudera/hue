<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:workflow="uri:oozie:workflow:0.1" exclude-result-prefixes="workflow">

<xsl:import href="fields/chmods.xslt"/>
<xsl:import href="fields/deletes.xslt"/>
<xsl:import href="fields/mkdirs.xslt"/>
<xsl:import href="fields/moves.xslt"/>
<xsl:import href="fields/touchzs.xslt"/>

<xsl:template match="workflow:fs" xmlns:workflow="uri:oozie:workflow:0.1">

  <object model="oozie.fs" pk="0">

    <xsl:call-template name="chmods"/>
    <xsl:call-template name="deletes"/>
    <xsl:call-template name="mkdirs"/>
    <xsl:call-template name="moves"/>
    <xsl:call-template name="touchzs"/>

  </object>

</xsl:template>

<xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes"/>
</xsl:stylesheet>