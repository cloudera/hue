<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:include href="action.xslt"/>
<xsl:include href="control.xslt"/>

<xsl:template match="/workflow-app">

  <django-objects version="1.0">

    <xsl:apply-templates select="action"/>
    <xsl:apply-templates select="start | end | decision | fork | join | kill"/>

  </django-objects>

</xsl:template>

<xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes"/>
</xsl:stylesheet>