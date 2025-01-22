<?xml version="1.0"?>
<samlp:Response xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol" xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" Version="2.0" ID="theresponse" IssueInstant="2020-12-04T07:48:09.700Z" InResponseTo="id-abc" Destination="https://example.org/acs/post">
    <saml:Issuer>urn:mace:example.com:saml:roland:idp</saml:Issuer>
    <samlp:Status>
        <samlp:StatusCode Value="urn:oasis:names:tc:SAML:2.0:status:Success"/>
    </samlp:Status>
    <saml:Assertion xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" Version="2.0" ID="theassertion" IssueInstant="2020-12-04T07:48:09.600Z">
        <saml:Issuer>urn:mace:example.com:saml:roland:idp</saml:Issuer>
        <ds:Signature xmlns:ds="http://www.w3.org/2000/09/xmldsig#">
            <ds:SignedInfo>
                <ds:CanonicalizationMethod Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"/>
                <ds:SignatureMethod Algorithm="http://www.w3.org/2000/09/xmldsig#hmac-sha1"/>
                <ds:Reference URI="#theassertion">
                    <ds:Transforms>
                        <ds:Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"/>
                        <ds:Transform Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"/>
                    </ds:Transforms>
                    <ds:DigestMethod Algorithm="http://www.w3.org/2001/04/xmlenc#sha256"/>
                    <ds:DigestValue>3eSifM9ENDpX4ore08DbmBaW3WrqLZMv57QMk0ACEPk=</ds:DigestValue>
                </ds:Reference>
            </ds:SignedInfo>
            <ds:SignatureValue>8v8fec9UyJ5g/GcZmkrG3gQT/eI=</ds:SignatureValue>
            <ds:KeyInfo>
                <ds:KeyValue>
                    <HMACKeyValue xmlns="http://www.aleksey.com/xmlsec/2002">Rk9PCg==</HMACKeyValue>
                </ds:KeyValue>
                <ds:X509Data>
                    <ds:X509Certificate>MIICXgIBAAKBgQDJg2cms7MqjniT8Fi/XkNHZNPbNVQyMUMXE9tXOdqwYCA1cc8vQdzkihscQMXy3iPw2cMggBu6gjMTOSOxECkuvX5ZCclKr8pXAJM5cY6gVOaVO2PdTZcvDBKGbiaNefiEw5hnoZomqZGp8wHNLAUkwtH9vjqqvxyS/vclc6k2ewIDAQABAoGBAKD2emW6ssmyhfQ9ztYFuJ4FlwiJf5icKuf7L4BsMRgjoHawUvt/k69l9aPKxZNrB7BycV+7lOqU57FaOf1MWGeWzsU5bYUVpFzOVwsY4umtsO78QGKLZe+91Z+ktOlmL3scAymAgE88Jmr0g8FC46Vv4Sam7zMCtmOvA9fYog1ZAkEA8lAe+XihSuZI6IZcdRdB6QJ5cgAJoZdWKKtUovb5Ah2w4D/ebkfpsQJK44aSR5GbnrnqSaMeLJMRz++Td0edHwJBANTlUBzoo3ihcBOZ0VzGYgDIG8foCTEf3jDBYNYaY9RH/c4P50GkDa4PBqtf1f+VORwAsC2NTeY6HUEWMpvfXyUCQQChQ3FZ1k6B6oDbP5CI3NGgoWTx2dSPFojgyCWrz3IpVllA5UDDZFjC1SPCCO2Rc/Z9zH2ARG7we3B/UpJx79dBAkEAiPc6sk6NFQevpjyYcDqFRIF5NgQ3Ha6l8PIITdZOkXz7cX3Txuw3jNrH7KtMbxDe3AApWDUHf+21cnFIf/WWLQJAeG0KKBfZw1iRu9vlcYakGWRUSga78QDy08uHDtxQLXxOfSvm/y8N1KrEsXf/cJzHUGQJrqk8nLzR5mTRqnAZWA==</ds:X509Certificate>
                </ds:X509Data>
            </ds:KeyInfo>
        </ds:Signature>
        <saml:Subject>
            <saml:NameID Format="urn:oasis:names:tc:SAML:2.0:nameid-format:persistent">attack-name-id</saml:NameID>
            <saml:SubjectConfirmation Method="urn:oasis:names:tc:SAML:2.0:cm:bearer">
                <saml:SubjectConfirmationData NotOnOrAfter="2020-12-04T07:58:09.600Z" Recipient="https://example.org/acs/post" InResponseTo="id-abc"/>
            </saml:SubjectConfirmation>
        </saml:Subject>
        <saml:Conditions NotBefore="2020-12-04T07:48:09.600Z" NotOnOrAfter="2020-12-04T07:58:09.600Z">
            <saml:AudienceRestriction>
                <saml:Audience>https://example.org/sp.xml</saml:Audience>
            </saml:AudienceRestriction>
        </saml:Conditions>
        <saml:AuthnStatement AuthnInstant="2020-12-04T07:48:09.600Z" SessionNotOnOrAfter="2020-12-04T07:58:09.600Z" SessionIndex="_samling_8227405_474676521">
            <saml:AuthnContext>
                <saml:AuthnContextClassRef>urn:oasis:names:tc:SAML:2.0:ac:classes:unspecified</saml:AuthnContextClassRef>
            </saml:AuthnContext>
        </saml:AuthnStatement>
    </saml:Assertion>
</samlp:Response>
