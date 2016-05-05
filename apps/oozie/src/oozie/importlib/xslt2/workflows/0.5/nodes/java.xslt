<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:workflow5="uri:oozie:workflow:0.5" xmlns:workflow4="uri:oozie:workflow:0.4">

<xsl:import href="fields/jar_path.xslt"/>

<xsl:template match="workflow5:java | workflow4:java" xmlns:workflow5="uri:oozie:workflow:0.5" xmlns:workflow4="uri:oozie:workflow:0.4">

  ,"java": {
        "main-class": "<xsl:value-of select="*[local-name()='main-class']"/>"
    }


</xsl:template>

</xsl:stylesheet>