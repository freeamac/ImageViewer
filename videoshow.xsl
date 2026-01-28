<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns="http://www.w3.org/TR/REC-html40">
  <xsl:output method="html" indent="yes"/>
  <xsl:template match="/videos">
    <HTML>
    <HEAD>
    <META http-equiv="Content-Type" content="text/html; charset=iso-8859-1"/>
    <TITLE><xsl:value-of select="title"/></TITLE>
    </HEAD>
    <BODY>
    <H1><xsl:value-of select="title"/></H1>
    <TABLE WIDTH="100%">
    <xsl:for-each select="video">
      <HR/>
      <TR WIDTH="100%">
        <TD WIDTH="50%" ALIGN="CENTER">
          <CENTER><xsl:value-of select="caption"/></CENTER>
          <xsl:element name="video">
	    <xsl:attribute name="height">540</xsl:attribute>
	    <xsl:attribute name="width">30</xsl:attribute>
	    <xsl:attribute name="controls"/>
	    <xsl:element name="source">
              <xsl:attribute name="src">
                <xsl:value-of select='source'/>
              </xsl:attribute>
            </xsl:element>
          </xsl:element>
	</TD>
      </TR>
    </xsl:for-each>
    </TABLE>
    <HR/>
    <xsl:value-of select="copyright"/>
    </BODY>
    </HTML>
  </xsl:template>
</xsl:stylesheet>
