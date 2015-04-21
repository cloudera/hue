<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:workflow="uri:oozie:workflow:0.5" xmlns:sqoop="uri:oozie:sqoop-action:0.1" exclude-result-prefixes="workflow sqoop">

<xsl:import href="../nodes/fields/script_path.xslt"/>

<xsl:template match="sqoop:sqoop">

  ,"sqoop": {<xsl:call-template name="script_path"/>}

</xsl:template>

</xsl:stylesheet>