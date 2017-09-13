import saml2
import saml2.xmlenc as xenc
from saml2 import xmldsig

data1 = """<?xml version='1.0' encoding='UTF-8'?>
<ns0:EncryptedData MimeType="text/xml" xmlns:ns0="http://www.w3.org/2001/04/xmlenc#">
    <ns0:CipherData>
        <ns0:CipherValue>A23B45C56</ns0:CipherValue>
    </ns0:CipherData>
</ns0:EncryptedData>"""


def test_1():
    ed = xenc.encrypted_data_from_string(data1)
    assert ed
    assert ed.mime_type == "text/xml"
    assert ed.cipher_data is not None
    cd = ed.cipher_data
    assert cd.cipher_value is not None
    assert cd.cipher_value.text == "A23B45C56"
    
data2 = """<?xml version='1.0' encoding='UTF-8'?>
<ns0:EncryptedData 
    Type="http://www.w3.org/2001/04/xmlenc#Element" 
    xmlns:ns0="http://www.w3.org/2001/04/xmlenc#">
    <ns0:EncryptionMethod Algorithm="http://www.w3.org/2001/04/xmlenc#tripledes-cbc" />
    <ns1:KeyInfo xmlns:ns1="http://www.w3.org/2000/09/xmldsig#">
        <ns1:KeyName>John Smith</ns1:KeyName>
    </ns1:KeyInfo>
    <ns0:CipherData>
        <ns0:CipherValue>DEADBEEF</ns0:CipherValue>
    </ns0:CipherData>
</ns0:EncryptedData>"""

# data2 = """<EncryptedData xmlns='http://www.w3.org/2001/04/xmlenc#'
#         Type='http://www.w3.org/2001/04/xmlenc#Element'>
#     <EncryptionMethod
#         Algorithm='http://www.w3.org/2001/04/xmlenc#tripledes-cbc'/>
#     <ds:KeyInfo xmlns:ds='http://www.w3.org/2000/09/xmldsig#'>
#         <ds:KeyName>John Smith</ds:KeyName>
#     </ds:KeyInfo>
#     <CipherData><CipherValue>DEADBEEF</CipherValue></CipherData>
# </EncryptedData>"""

def test_2():
    ed = xenc.encrypted_data_from_string(data2)
    assert ed
    print(ed)
    assert ed.type == "http://www.w3.org/2001/04/xmlenc#Element"
    assert ed.encryption_method is not None
    em = ed.encryption_method
    assert em.algorithm == 'http://www.w3.org/2001/04/xmlenc#tripledes-cbc'
    assert ed.key_info is not None
    ki = ed.key_info
    assert ki.key_name[0].text == "John Smith"
    assert ed.cipher_data is not None
    cd = ed.cipher_data
    assert cd.cipher_value is not None
    assert cd.cipher_value.text == "DEADBEEF"

data3 = """<?xml version='1.0' encoding='UTF-8'?>
<ns0:EncryptedData 
    Id="ED" 
    xmlns:ns0="http://www.w3.org/2001/04/xmlenc#">
    <ns0:EncryptionMethod Algorithm="http://www.w3.org/2001/04/xmlenc#aes128-cbc" />
    <ns1:KeyInfo xmlns:ns1="http://www.w3.org/2000/09/xmldsig#">
        <ns1:RetrievalMethod URI='#EK'
            Type="http://www.w3.org/2001/04/xmlenc#EncryptedKey"/>
        <ns1:KeyName>Sally Doe</ns1:KeyName>
    </ns1:KeyInfo>
    <ns0:CipherData>
        <ns0:CipherValue>DEADBEEF</ns0:CipherValue>
    </ns0:CipherData>
</ns0:EncryptedData>"""

def test_3():
    ed = xenc.encrypted_data_from_string(data3)
    assert ed
    print(ed)
    assert ed.encryption_method != None
    em = ed.encryption_method
    assert em.algorithm == 'http://www.w3.org/2001/04/xmlenc#aes128-cbc'
    assert ed.key_info != None
    ki = ed.key_info
    assert ki.key_name[0].text == "Sally Doe"
    assert len(ki.retrieval_method) == 1
    rm = ki.retrieval_method[0]
    assert rm.uri == "#EK"
    assert rm.type == "http://www.w3.org/2001/04/xmlenc#EncryptedKey"
    assert ed.cipher_data != None
    cd = ed.cipher_data
    assert cd.cipher_value != None
    assert cd.cipher_value.text == "DEADBEEF"

data4 = """<?xml version='1.0' encoding='UTF-8'?>
<ns0:EncryptedKey 
    Id="EK" 
    xmlns:ns0="http://www.w3.org/2001/04/xmlenc#">
    <ns0:EncryptionMethod Algorithm="http://www.w3.org/2001/04/xmlenc#rsa-1_5" />
    <ns1:KeyInfo xmlns:ns1="http://www.w3.org/2000/09/xmldsig#">
        <ns1:KeyName>John Smith</ns1:KeyName>
    </ns1:KeyInfo>
    <ns0:CipherData>
        <ns0:CipherValue>xyzabc</ns0:CipherValue>
    </ns0:CipherData>
    <ns0:ReferenceList>
        <ns0:DataReference URI='#ED'/>
    </ns0:ReferenceList>
    <ns0:CarriedKeyName>Sally Doe</ns0:CarriedKeyName>
</ns0:EncryptedKey>"""


# data4 = """<EncryptedKey Id='EK' xmlns='http://www.w3.org/2001/04/xmlenc#'>
#     <EncryptionMethod 
#            Algorithm="http://www.w3.org/2001/04/xmlenc#rsa-1_5"/>
#     <ds:KeyInfo xmlns:ds='http://www.w3.org/2000/09/xmldsig#'>
#         <ds:KeyName>John Smith</ds:KeyName>
#     </ds:KeyInfo>
#     <CipherData><CipherValue>xyzabc</CipherValue></CipherData>
#     <ReferenceList>
#         <DataReference URI='#ED'/>
#     </ReferenceList>
#     <CarriedKeyName>Sally Doe</CarriedKeyName>
# </EncryptedKey>"""

def test_4():
    ek = xenc.encrypted_key_from_string(data4)
    assert ek
    print(ek)
    assert ek.encryption_method != None
    em = ek.encryption_method
    assert em.algorithm == 'http://www.w3.org/2001/04/xmlenc#rsa-1_5'
    assert ek.key_info != None
    ki = ek.key_info
    assert ki.key_name[0].text == "John Smith"
    assert ek.reference_list != None
    rl = ek.reference_list
    assert len(rl.data_reference)
    dr = rl.data_reference[0]
    assert dr.uri == "#ED"
    assert ek.cipher_data != None
    cd = ek.cipher_data
    assert cd.cipher_value != None
    assert cd.cipher_value.text == "xyzabc"

data5 = """<CipherReference URI="http://www.example.com/CipherValues.xml"
    xmlns="http://www.w3.org/2001/04/xmlenc#">
    <Transforms xmlns:ds='http://www.w3.org/2000/09/xmldsig#'>
        <ds:Transform 
           Algorithm="http://www.w3.org/TR/1999/REC-xpath-19991116">
           <ds:XPath xmlns:rep="http://www.example.org/repository">
             self::text()[parent::rep:CipherValue[@Id="example1"]]
           </ds:XPath>
        </ds:Transform>
        <ds:Transform Algorithm="http://www.w3.org/2000/09/xmldsig#base64"/>
    </Transforms>
</CipherReference>"""

def test_5():
    cr = xenc.cipher_reference_from_string(data5)
    assert cr
    print(cr)
    print(cr.keyswv())
    trs = cr.transforms
    assert len(trs.transform) == 2
    tr = trs.transform[0]
    assert tr.algorithm in ["http://www.w3.org/TR/1999/REC-xpath-19991116",
            "http://www.w3.org/2000/09/xmldsig#base64"]
    if tr.algorithm == "http://www.w3.org/2000/09/xmldsig#base64":
        pass
    elif tr.algorithm == "http://www.w3.org/TR/1999/REC-xpath-19991116":
        assert len(tr.x_path) == 1
        xp = tr.x_path[0]
        assert xp.text.strip() == """self::text()[parent::rep:CipherValue[@Id="example1"]]"""
        
        
data6 = """<ReferenceList xmlns="http://www.w3.org/2001/04/xmlenc#">
    <DataReference URI="#invoice34">
      <ds:Transforms xmlns:ds='http://www.w3.org/2000/09/xmldsig#'>
        <ds:Transform Algorithm="http://www.w3.org/TR/1999/REC-xpath-19991116">
          <ds:XPath xmlns:xenc="http://www.w3.org/2001/04/xmlenc#">
              self::xenc:EncryptedData[@Id="example1"]
          </ds:XPath>
        </ds:Transform>
      </ds:Transforms>
    </DataReference>
</ReferenceList>"""

def test_6():
    rl = xenc.reference_list_from_string(data6)
    assert rl
    print(rl)
    assert len(rl.data_reference) == 1
    dr = rl.data_reference[0]
    assert dr.uri == "#invoice34"
    assert len(dr.extension_elements) == 1
    ee = dr.extension_elements[0]
    assert ee.tag == "Transforms"
    assert ee.namespace == "http://www.w3.org/2000/09/xmldsig#"
    trs = saml2.extension_element_to_element(ee, xmldsig.ELEMENT_FROM_STRING,
                                        namespace=xmldsig.NAMESPACE)
    
    assert trs
    assert len(trs.transform) == 1
    tr = trs.transform[0]
    assert tr.algorithm == "http://www.w3.org/TR/1999/REC-xpath-19991116"
    assert len(tr.x_path) == 1
    assert tr.x_path[0].text.strip() == """self::xenc:EncryptedData[@Id="example1"]"""

