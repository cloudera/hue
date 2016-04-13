<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:workflow="uri:oozie:workflow:0.5" xmlns:spark="uri:oozie:spark-action:0.1" exclude-result-prefixes="workflow spark">

<xsl:template match="spark:spark">

  ,"spark": {
    "name": "<xsl:value-of select="*[local-name()='name']"/>",
    "master": "<xsl:value-of select="*[local-name()='master']"/>",
    "mode": "<xsl:value-of select="*[local-name()='mode']"/>",
    "class": "<xsl:value-of select="*[local-name()='class']"/>",
    "jar": "<xsl:value-of select="*[local-name()='jar']"/>"
  }

</xsl:template>

</xsl:stylesheet>