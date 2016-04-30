<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:workflow="uri:oozie:workflow:0.5" exclude-result-prefixes="workflow">

<xsl:import href="nodes/fork.xslt"/>
<xsl:import href="nodes/decision.xslt"/>

<xsl:template match="workflow:start | workflow:end | workflow:decision | workflow:fork | workflow:join | workflow:kill">
  {
    "name": "<xsl:value-of select="@name"/>",
    "node_type": "<xsl:value-of select="name(.)"/>",
    "ok_to": "<xsl:value-of select="@to"/>"

    <xsl:apply-imports/>
  },
</xsl:template>

</xsl:stylesheet>