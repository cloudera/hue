<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:template name="reducer">

  "reducer": "<xsl:value-of select="*[local-name()='streaming']/*[local-name()='reducer']"/>"

</xsl:template>
</xsl:stylesheet>