<?xml version="1.0"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:template name="java_opts">

  <field name="java_opts" type="CharField">
    <xsl:value-of select="*[local-name()='java-opts']"/>
  </field>

</xsl:template>

</xsl:stylesheet>