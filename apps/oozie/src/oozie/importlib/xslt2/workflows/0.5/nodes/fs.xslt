<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:workflow="uri:oozie:workflow:0.5" exclude-result-prefixes="workflow">

<xsl:import href="fields/touchzs.xslt"/>

<xsl:template match="workflow:fs" xmlns:workflow="uri:oozie:workflow:0.5">

  ,"fs": { <xsl:call-template name="touchzs"/> }

</xsl:template>

</xsl:stylesheet>