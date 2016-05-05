<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:workflow5="uri:oozie:workflow:0.5" xmlns:workflow4="uri:oozie:workflow:0.4">

<xsl:import href="fields/script_path.xslt"/>

<xsl:template match="workflow5:pig | workflow4:pig" xmlns:workflow5="uri:oozie:workflow:0.5" xmlns:workflow4="uri:oozie:workflow:0.4">

  ,"pig": {<xsl:call-template name="script_path"/>}

</xsl:template>

</xsl:stylesheet>