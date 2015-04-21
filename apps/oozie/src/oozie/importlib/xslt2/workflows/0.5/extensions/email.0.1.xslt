<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:workflow="uri:oozie:workflow:0.5" xmlns:email="uri:oozie:email-action:0.1" exclude-result-prefixes="workflow email">

<xsl:template match="email:email">

  ,"email": {"subject": "<xsl:value-of select="*[local-name()='subject']"/>"}

</xsl:template>

</xsl:stylesheet>