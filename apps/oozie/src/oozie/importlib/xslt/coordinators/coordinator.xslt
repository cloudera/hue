<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:coordinator="uri:oozie:coordinator:0.1" exclude-result-prefixes="coordinator">

<xsl:include href="0.1/coordinator.xslt"/>
<xsl:include href="0.2/coordinator.xslt"/>
<xsl:include href="0.3/coordinator.xslt"/>
<xsl:include href="0.4/coordinator.xslt"/>

<xsl:template match="/">

    <xsl:apply-templates select="*"/>

</xsl:template>

<xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes"/>
</xsl:stylesheet>