<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:workflow="uri:oozie:workflow:0.2" exclude-result-prefixes="workflow">

<xsl:template name="job_xml">

  <field name="job_xml" type="CharField">
    <xsl:value-of select="*[local-name()='job-xml']"/>
  </field>

</xsl:template>

</xsl:stylesheet>