<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:workflow5="uri:oozie:workflow:0.5" xmlns:workflow4="uri:oozie:workflow:0.4" xmlns:workflow3="uri:oozie:workflow:0.3" xmlns:workflow2="uri:oozie:workflow:0.2" xmlns:workflow1="uri:oozie:workflow:0.1">

<xsl:import href="fields/script_path.xslt"/>

<xsl:template match="workflow5:pig | workflow4:pig | workflow3:pig | workflow2:pig | workflow1:pig" xmlns:workflow5="uri:oozie:workflow:0.5" xmlns:workflow4="uri:oozie:workflow:0.4" xmlns:workflow3="uri:oozie:workflow:0.3" xmlns:workflow2="uri:oozie:workflow:0.2" xmlns:workflow1="uri:oozie:workflow:0.1">

  ,"pig": {<xsl:call-template name="script_path"/>}

</xsl:template>

</xsl:stylesheet>