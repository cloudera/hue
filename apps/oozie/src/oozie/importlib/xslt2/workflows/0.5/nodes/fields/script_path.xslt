<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:template name="script_path">

  "script_path": "<xsl:value-of select="*[local-name()='script']"/>"

</xsl:template>

</xsl:stylesheet>