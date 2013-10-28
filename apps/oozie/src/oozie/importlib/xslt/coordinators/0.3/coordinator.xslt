<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:coordinator="uri:oozie:coordinator:0.3" exclude-result-prefixes="coordinator">

<xsl:include href="dataset.xslt"/>
<xsl:include href="datainput.xslt"/>
<xsl:include href="dataoutput.xslt"/>

<xsl:template match="/coordinator:coordinator-app">

  <django-objects version="1.0">

    <xsl:apply-templates select="coordinator:datasets/coordinator:dataset"/>
    <xsl:apply-templates select="coordinator:input-events/coordinator:data-in"/>
    <xsl:apply-templates select="coordinator:output-events/coordinator:data-out"/>

  </django-objects>

</xsl:template>

<xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes"/>
</xsl:stylesheet>