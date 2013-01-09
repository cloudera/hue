<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:workflow="uri:oozie:workflow:0.3" exclude-result-prefixes="workflow">

<xsl:import href="fields/xml.xslt"/>

<xsl:template match="workflow:*[local-name()!='decision' and local-name()!='end' and local-name()!='fork' and local-name()!='fs' and local-name()!='java' and local-name()!='join' and local-name()!='kill' and local-name()!='map-reduce' and local-name()!='pig' and local-name()!='start' and local-name()!='streaming' and local-name()!='subworkflow' and local-name()!='distcp' and local-name()!='email' and local-name()!='hive' and local-name()!='shell' and local-name()!='sqoop' and local-name()!='ssh' and local-name()!='ok' and local-name()!='error']" xmlns:workflow="uri:oozie:workflow:0.3">

  <object model="oozie.generic" pk="0">

    <xsl:call-template name="xml"/>

  </object>

</xsl:template>

<xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes"/>
</xsl:stylesheet>