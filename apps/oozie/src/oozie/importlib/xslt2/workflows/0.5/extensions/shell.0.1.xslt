<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:workflow="uri:oozie:workflow:0.5" xmlns:shell="uri:oozie:shell-action:0.1" exclude-result-prefixes="workflow shell">

<xsl:import href="../nodes/fields/command.xslt"/>

<xsl:template match="shell:shell">

  ,"shell": {<xsl:call-template name="command"/>}

</xsl:template>

</xsl:stylesheet>