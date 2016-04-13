<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:workflow="uri:oozie:workflow:0.5" exclude-result-prefixes="workflow">

<xsl:import href="fields/jar_path.xslt"/>

<xsl:template match="workflow:java" xmlns:workflow="uri:oozie:workflow:0.5">

  ,"java": {
        "main-class": "<xsl:value-of select="*[local-name()='main-class']"/>"
    }


</xsl:template>

</xsl:stylesheet>