<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:workflow="uri:oozie:workflow:0.3" xmlns:sqoop="uri:oozie:sqoop-action:0.2" exclude-result-prefixes="workflow sqoop">

<xsl:import href="../nodes/fields/archives.xslt"/>
<xsl:import href="../nodes/fields/files.xslt"/>
<xsl:import href="../nodes/fields/job_properties.xslt"/>
<xsl:import href="../nodes/fields/job_xml.xslt"/>
<xsl:import href="../nodes/fields/arg_params.xslt"/>
<xsl:import href="../nodes/fields/prepares.xslt"/>

<xsl:template match="sqoop:sqoop">

  <object model="oozie.sqoop" pk="0">

    <xsl:call-template name="archives"/>
    <xsl:call-template name="files"/>
    <xsl:call-template name="job_properties"/>
    <xsl:call-template name="job_xml"/>
    <xsl:call-template name="arg_params"/>
    <xsl:call-template name="prepares"/>
    <field name="script_path" type="CharField">
      <xsl:value-of select="*[local-name()='command']"/>
    </field>

  </object>

</xsl:template>

<xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes"/>
</xsl:stylesheet>