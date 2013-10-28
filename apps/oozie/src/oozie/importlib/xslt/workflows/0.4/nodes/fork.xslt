<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:workflow="uri:oozie:workflow:0.4" exclude-result-prefixes="workflow">

<xsl:template match="workflow:fork" xmlns:workflow="uri:oozie:workflow:0.4">

  <object model="oozie.fork" pk="0">
  </object>

</xsl:template>

<xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes"/>
</xsl:stylesheet>