<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:workflow5="uri:oozie:workflow:0.5" xmlns:workflow4="uri:oozie:workflow:0.4">

<xsl:template match="workflow5:sub-workflow | workflow4:sub-workflow" xmlns:workflow5="uri:oozie:workflow:0.5" xmlns:workflow4="uri:oozie:workflow:0.4">
  , "subworkflow": { "app-path":"<xsl:value-of select="*[local-name()='app-path']"/>" }
</xsl:template>

</xsl:stylesheet>