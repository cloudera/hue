<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:sqoop="uri:oozie:sqoop-action:0.4">

<xsl:template match="sqoop:sqoop">

  ,"sqoop": {"command": "<xsl:value-of select="*[local-name()='command']"/>"}

</xsl:template>

</xsl:stylesheet>