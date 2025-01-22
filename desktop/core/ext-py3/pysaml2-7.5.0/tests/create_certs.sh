#!/bin/sh
newcert="openssl req -x509 -new -days 365000 -sha256 -config openssl.cnf -set_serial 1"
$newcert -key test_1.key -out test_1.crt -subj '/C=zz/ST=zz/L=zzzz/O=Zzzzz/OU=Zzzzz/CN=test'
$newcert -key test_2.key -out test_2.crt -subj '/C=zz/ST=zz/L=zzzz/O=Zzzzz/OU=Zzzzz/CN=test'
$newcert -key pki/test_3.key -out pki/test_3.crt -subj '/C=zz/ST=zz/L=zzzz/O=Zzzzz/OU=Zzzzz/CN=test'
$newcert -key root_cert/localhost.ca.key -out root_cert/localhost.ca.crt -subj '/C=se/ST=ac/L=umea/O=ITS Umea University/OU=DIRG/CN=localhost.ca'
