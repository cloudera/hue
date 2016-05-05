<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:template name="command">
  "command":"<xsl:value-of select="*[local-name()='exec']"/>"
</xsl:template>

</xsl:stylesheet>