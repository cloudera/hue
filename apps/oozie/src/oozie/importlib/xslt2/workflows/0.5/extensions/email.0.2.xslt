<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:email="uri:oozie:email-action:0.2">

<xsl:template match="email:email">

  ,"email": {
    "to": "<xsl:value-of select="*[local-name()='to']"/>",
    "subject": "<xsl:value-of select="*[local-name()='subject']"/>"
   }

</xsl:template>

</xsl:stylesheet>