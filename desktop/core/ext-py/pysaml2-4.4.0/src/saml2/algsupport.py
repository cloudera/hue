from subprocess import Popen, PIPE
from saml2.sigver import get_xmlsec_binary
from saml2.extension.algsupport import SigningMethod
from saml2.extension.algsupport import DigestMethod

__author__ = 'roland'

DIGEST_METHODS = {
    "hmac-md5": 'http://www.w3.org/2001/04/xmldsig-more#md5', # test framework only!
    "hmac-sha1": 'http://www.w3.org/2000/09/xmldsig#sha1',
    "hmac-sha224": 'http://www.w3.org/2001/04/xmldsig-more#sha224',
    "hmac-sha256": 'http://www.w3.org/2001/04/xmlenc#sha256',
    "hmac-sha384": 'http://www.w3.org/2001/04/xmldsig-more#sha384',
    "hmac-sha512": 'http://www.w3.org/2001/04/xmlenc#sha512',
    "hmac-ripemd160": 'http://www.w3.org/2001/04/xmlenc#ripemd160'
}

SIGNING_METHODS = {
    "rsa-md5": 'http://www.w3.org/2001/04/xmldsig-more#rsa-md5',
    "rsa-ripemd160": 'http://www.w3.org/2001/04/xmldsig-more#rsa-ripemd160',
    "rsa-sha1": 'http://www.w3.org/2000/09/xmldsig#rsa-sha1',
    "rsa-sha224": 'http://www.w3.org/2001/04/xmldsig-more#rsa-sha224',
    "rsa-sha256": 'http://www.w3.org/2001/04/xmldsig-more#rsa-sha256',
    "rsa-sha384": 'http://www.w3.org/2001/04/xmldsig-more#rsa-sha384',
    "rsa-sha512": 'http://www.w3.org/2001/04/xmldsig-more#rsa-sha512',
    "dsa-sha1": 'http,//www.w3.org/2000/09/xmldsig#dsa-sha1',
    'dsa-sha256': 'http://www.w3.org/2009/xmldsig11#dsa-sha256',
    'ecdsa_sha1': 'http://www.w3.org/2001/04/xmldsig-more#ECDSA_sha1',
    'ecdsa_sha224': 'http://www.w3.org/2001/04/xmldsig-more#ECDSA_sha224',
    'ecdsa_sha256': 'http://www.w3.org/2001/04/xmldsig-more#ECDSA_sha256',
    'ecdsa_sha384': 'http://www.w3.org/2001/04/xmldsig-more#ECDSA_sha384',
    'ecdsa_sha512': 'http://www.w3.org/2001/04/xmldsig-more#ECDSA_sha512',
}


def get_algorithm_support(xmlsec):
    com_list = [xmlsec, '--list-transforms']
    pof = Popen(com_list, stderr=PIPE, stdout=PIPE)

    p_out = pof.stdout.read().decode('utf-8')
    p_err = pof.stderr.read().decode('utf-8')
    pof.wait()

    if not p_err:
        p = p_out.splitlines()
        algs = [x.strip('"') for x in p[1].split(',')]
        digest = []
        signing = []
        for alg in algs:
            if alg in DIGEST_METHODS:
                digest.append(alg)
            elif alg in SIGNING_METHODS:
                signing.append(alg)

        return {"digest": digest, "signing": signing}

    raise SystemError(p_err)


def algorithm_support_in_metadata(xmlsec):
    if xmlsec is None:
        return []

    support = get_algorithm_support(xmlsec)
    element_list = []
    for alg in support["digest"]:
        element_list.append(DigestMethod(algorithm=DIGEST_METHODS[alg]))
    for alg in support["signing"]:
        element_list.append(SigningMethod(algorithm=SIGNING_METHODS[alg]))
    return element_list

if __name__ == '__main__':
    xmlsec = get_xmlsec_binary()
    res = get_algorithm_support(xmlsec)
    print(res)
    for a in algorithm_support_in_metadata(xmlsec):
        print(a)
