<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:workflow="uri:oozie:workflow:0.5" exclude-result-prefixes="workflow">

<xsl:import href="fields/script_path.xslt"/>

<xsl:template match="workflow:pig" xmlns:workflow="uri:oozie:workflow:0.5">

  ,"pig": {<xsl:call-template name="script_path"/>}

</xsl:template>

</xsl:stylesheet>