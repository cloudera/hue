<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:workflow="uri:oozie:workflow:0.5" xmlns:hive="uri:oozie:hive-action:0.2" exclude-result-prefixes="workflow hive">

<xsl:import href="../nodes/fields/script_path.xslt"/>

<xsl:template match="hive:hive">

  ,"hive": {<xsl:call-template name="script_path"/>}

</xsl:template>

</xsl:stylesheet>