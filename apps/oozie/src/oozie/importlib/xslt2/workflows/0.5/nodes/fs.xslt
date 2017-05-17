<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:workflow5="uri:oozie:workflow:0.5" xmlns:workflow4="uri:oozie:workflow:0.4" xmlns:workflow3="uri:oozie:workflow:0.3" xmlns:workflow2="uri:oozie:workflow:0.2" xmlns:workflow1="uri:oozie:workflow:0.1">

<xsl:import href="fields/touchzs.xslt"/>
<xsl:import href="fields/deletes.xslt"/>
<xsl:import href="fields/mkdirs.xslt"/>
<xsl:import href="fields/moves.xslt"/>

<xsl:template match="workflow5:fs | workflow4:fs | workflow3:fs | workflow2:fs | workflow1:fs" xmlns:workflow5="uri:oozie:workflow:0.5" xmlns:workflow4="uri:oozie:workflow:0.4" xmlns:workflow3="uri:oozie:workflow:0.3" xmlns:workflow2="uri:oozie:workflow:0.2" xmlns:workflow1="uri:oozie:workflow:0.1">

  ,"fs": { <xsl:call-template name="touchzs"/>,
           <xsl:call-template name="deletes"/>,
           <xsl:call-template name="mkdirs"/>,
           <xsl:call-template name="moves"/> }

</xsl:template>

</xsl:stylesheet>