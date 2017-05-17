<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:workflow5="uri:oozie:workflow:0.5" xmlns:workflow4="uri:oozie:workflow:0.4" xmlns:workflow3="uri:oozie:workflow:0.3" xmlns:workflow2="uri:oozie:workflow:0.2" xmlns:workflow1="uri:oozie:workflow:0.1">

<xsl:import href="fields/mapper.xslt"/>
<xsl:import href="fields/reducer.xslt"/>

<xsl:template name="streaming">

  ,"streaming": {
        "mapper": "<xsl:value-of select="*[local-name()='map-reduce']/*[local-name()='streaming']/*[local-name()='mapper']"/>",
        "reducer": "<xsl:value-of select="*[local-name()='map-reduce']/*[local-name()='streaming']/*[local-name()='reducer']"/>"
    }

</xsl:template>

</xsl:stylesheet>