<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:workflow5="uri:oozie:workflow:0.5" xmlns:workflow4="uri:oozie:workflow:0.4" xmlns:workflow3="uri:oozie:workflow:0.3" xmlns:workflow2="uri:oozie:workflow:0.2" xmlns:workflow1="uri:oozie:workflow:0.1">

<xsl:import href="nodes/fork.xslt"/>
<xsl:import href="nodes/decision.xslt"/>

<xsl:template match="workflow5:start | workflow5:end | workflow5:decision | workflow5:fork | workflow5:join | workflow5:kill | workflow4:start | workflow4:end | workflow4:decision | workflow4:fork | workflow4:join | workflow4:kill | workflow3:start | workflow3:end | workflow3:decision | workflow3:fork | workflow3:join | workflow3:kill | workflow2:start | workflow2:end | workflow2:decision | workflow2:fork | workflow2:join | workflow2:kill | workflow1:start | workflow1:end | workflow1:decision | workflow1:fork | workflow1:join | workflow1:kill">
  {
    "name": "<xsl:value-of select="@name"/>",
    "node_type": "<xsl:value-of select="name(.)"/>",
    "ok_to": "<xsl:value-of select="@to"/>"

    <xsl:apply-imports/>
  },
</xsl:template>

</xsl:stylesheet>