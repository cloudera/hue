# PEM Decoder and Encoder

Often times DER-encoded data is wrapped in PEM encoding. This allows the binary
DER data to be identified and reliably sent over various communication channels.

The `asn1crypto.pem` module includes three functions:

 - `detect(byte_string)`
 - `unarmor(pem_bytes, multiple=False)`
 - `armor(type_name, der_bytes, headers=None)`

## detect()

The `detect()` function accepts a byte string and looks for a `BEGIN` block
line. This is useful to determine in a byte string needs to be PEM-decoded
before parsing.

```python
from asn1crypto import pem, x509

with open('/path/to/cert', 'rb') as f:
    der_bytes = f.read()
    if pem.detect(der_bytes):
        _, _, der_bytes = pem.unarmor(der_bytes)
```

## unarmor()

The `unarmor()` function accepts a byte string and the flag to indicates if
more than one PEM block may be contained in the byte string. The result is
a three-element tuple.

 - The first element is a unicode string of the type of PEM block. Examples
   include: `CERTIFICATE`, `PRIVATE KEY`, `PUBLIC KEY`.
 - The second element is a `dict` of PEM block headers. Headers are typically
   only used by encrypted OpenSSL private keys, and are in the format
   `Name: Value`.
 - The third element is a byte string of the decoded block contents.

```python
from asn1crypto import pem, x509

with open('/path/to/cert', 'rb') as f:
    der_bytes = f.read()
    if pem.detect(der_bytes):
        type_name, headers, der_bytes = pem.unarmor(der_bytes)

cert = x509.Certificate.load(der_bytes)
```

If the `multiple` keyword argument is set to `True`, a generator will be
returned.

```python
from asn1crypto import pem, x509

certs = []
with open('/path/to/ca_certs', 'rb') as f:
    for type_name, headers, der_bytes in pem.unarmor(f.read(), multiple=True):
        certs.append(x509.Certificate.load(der_bytes))
```

## armor()

The `armor()` function accepts three parameters: a unicode string of the block
type name, a byte string to encode and an optional keyword argument `headers`,
that should be a `dict` of headers to add after the `BEGIN` line. Headers are
typically only used by encrypted OpenSSL private keys.

```python
from asn1crypto import pem, x509

# cert is an instance of x509.Certificate

with open('/path/to/cert', 'wb') as f:
    der_bytes = cert.dump()
    pem_bytes = pem.armor('CERTIFICATE', der_bytes)
    f.write(pem_bytes)
```
