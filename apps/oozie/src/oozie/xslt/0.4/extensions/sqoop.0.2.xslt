<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:import href="../fields/archives.xslt"/>
<xsl:import href="../fields/files.xslt"/>
<xsl:import href="../fields/job_properties.xslt"/>
<xsl:import href="../fields/job_xml.xslt"/>
<xsl:import href="../fields/params.xslt"/>
<xsl:import href="../fields/prepares.xslt"/>

<xsl:template match="sqoop:sqoop" xmlns:sqoop="uri:oozie:sqoop-action:0.2">

  <object model="oozie.sqoop" pk="0">

    <xsl:call-template name="archives"/>
    <xsl:call-template name="files"/>
    <xsl:call-template name="job_properties"/>
    <xsl:call-template name="job_xml"/>
    <xsl:call-template name="params"/>
    <xsl:call-template name="prepares"/>
    <field name="script_path" type="CharField">
      <xsl:value-of select="*[local-name()='command']"/>
    </field>

  </object>

</xsl:template>

<xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes"/>
</xsl:stylesheet>