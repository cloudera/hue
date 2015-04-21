<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:workflow="uri:oozie:workflow:0.5" xmlns:sqoop="uri:oozie:sqoop-action:0.2" exclude-result-prefixes="workflow sqoop">

<xsl:template match="sqoop:sqoop">

  ,"sqoop": {"script_path": "<xsl:value-of select="*[local-name()='command']"/>"}

</xsl:template>

</xsl:stylesheet>