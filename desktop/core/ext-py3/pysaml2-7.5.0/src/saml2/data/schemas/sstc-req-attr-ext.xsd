<?xml version="1.0" encoding="UTF-8"?>
<!-- 
     SAML v2.0 Protocol Extension for Requesting Attributes per Request Version 1.0
     Committee Specification 01
     23 August 2017
     Copyright (c) OASIS Open 2017. All Rights Reserved.
     Source: http://docs.oasis-open.org/security/saml-protoc-req-attr-req/v1.0/cs01/schema/
     Latest version of the specification: http://docs.oasis-open.org/security/saml-protoc-req-attr-req/v1.0/saml-protoc-req-attr-req-v1.0.html
     TC IPR Statement: https://www.oasis-open.org/committees/security/ipr.php
-->

<schema xmlns:req-attr="urn:oasis:names:tc:SAML:protocol:ext:req-attr"
         targetNamespace="urn:oasis:names:tc:SAML:protocol:ext:req-attr"
         xmlns:md="urn:oasis:names:tc:SAML:2.0:metadata"
         xmlns="http://www.w3.org/2001/XMLSchema"
         elementFormDefault="unqualified"
		 attributeFormDefault="unqualified"
		 blockDefault="substitution"
		 version="1.0">

   <import namespace="urn:oasis:names:tc:SAML:2.0:metadata"
		schemaLocation="saml-schema-metadata-2.0.xsd"/>

   <annotation>
       <documentation>
           Document title: SAML V2.0 Protocol Extension For Requesting Attributes Per Request
           Document identifier: sstc-req-attr-ext
           Location: http://docs.oasis-open.org/security/saml-protoc-req-attr-req/v1.0/csprd01/schema/
           Revision history: WD-03
       </documentation>
   </annotation>


   <element name="RequestedAttributes" type="req-attr:RequestedAttributesType"/>

   <complexType name="RequestedAttributesType">
       <sequence>
           <element ref="md:RequestedAttribute" minOccurs="1" maxOccurs="unbounded"/>
       </sequence>
   </complexType>

   <attribute name="supportsRequestedAttributes" type="boolean"/>
</schema>
