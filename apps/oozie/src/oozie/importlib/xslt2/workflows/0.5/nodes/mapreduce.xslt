<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:workflow5="uri:oozie:workflow:0.5" xmlns:workflow4="uri:oozie:workflow:0.4" xmlns:workflow3="uri:oozie:workflow:0.3" xmlns:workflow2="uri:oozie:workflow:0.2" xmlns:workflow1="uri:oozie:workflow:0.1">

<xsl:import href="fields/job_properties.xslt"/>

<xsl:template match="workflow5:map-reduce | workflow4:map-reduce | workflow3:map-reduce | workflow2:map-reduce | workflow1:map-reduce" xmlns:workflow5="uri:oozie:workflow:0.5" xmlns:workflow4="uri:oozie:workflow:0.4" xmlns:workflow3="uri:oozie:workflow:0.3" xmlns:workflow2="uri:oozie:workflow:0.2" xmlns:workflow1="uri:oozie:workflow:0.1">

    <xsl:call-template name="job_properties"/>

</xsl:template>

</xsl:stylesheet>