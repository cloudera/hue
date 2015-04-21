<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:workflow="uri:oozie:workflow:0.5" xmlns:ssh="uri:oozie:ssh-action:0.1" exclude-result-prefixes="workflow ssh">

<xsl:import href="../nodes/fields/command.xslt"/>

<xsl:template match="ssh:ssh">

  ,"ssh": "<xsl:call-template name="command"/>"

</xsl:template>

</xsl:stylesheet>