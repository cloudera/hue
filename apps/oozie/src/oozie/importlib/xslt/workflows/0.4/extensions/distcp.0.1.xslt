<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:workflow="uri:oozie:workflow:0.4" xmlns:distcp="uri:oozie:distcp-action:0.1" exclude-result-prefixes="workflow distcp">

<xsl:import href="../nodes/fields/job_properties.xslt"/>
<xsl:import href="../nodes/fields/job_xml.xslt"/>
<xsl:import href="../nodes/fields/params.xslt"/>
<xsl:import href="../nodes/fields/prepares.xslt"/>

<xsl:template match="distcp:distcp">

  <object model="oozie.distcp" pk="0">

    <xsl:call-template name="job_properties"/>
    <xsl:call-template name="job_xml"/>
    <field name="params" type="CharField">
      <xsl:text>[</xsl:text>
      <xsl:for-each select="*[local-name()='arg']">
        <xsl:choose>
          <xsl:when test="position() &lt; last()">
            <xsl:text><![CDATA[{"type":"arg","value":"]]></xsl:text><xsl:value-of select="." /><xsl:text><![CDATA["},]]></xsl:text>
          </xsl:when>
          <xsl:otherwise>
            <xsl:text><![CDATA[{"type":"arg","value":"]]></xsl:text><xsl:value-of select="." /><xsl:text><![CDATA["}]]></xsl:text>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:for-each>
      <xsl:text>]</xsl:text>
    </field>
    <xsl:call-template name="prepares"/>

  </object>

</xsl:template>

<xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes"/>
</xsl:stylesheet>