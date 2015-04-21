<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:workflow="uri:oozie:workflow:0.5" exclude-result-prefixes="workflow">

<xsl:import href="fields/mapper.xslt"/>
<xsl:import href="fields/reducer.xslt"/>

<xsl:template match="workflow:streaming" xmlns:workflow="uri:oozie:workflow:0.5">

  ,"streaming": {
        <xsl:call-template name="mapper"/>,
        <xsl:call-template name="reducer"/> }

</xsl:template>

</xsl:stylesheet>