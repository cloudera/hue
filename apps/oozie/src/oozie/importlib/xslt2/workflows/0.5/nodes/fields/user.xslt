<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:template name="user">

  "user": "<xsl:value-of select="*[local-name()='user']"/>"

</xsl:template>

</xsl:stylesheet>