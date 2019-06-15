---
title: "Server"
date: 2019-03-13T18:28:09-07:00
draft: false
weight: 1
---

This section is about configuring the Hue server itself.
These configuration variables are under the `[desktop]` section in
the `conf/hue.ini` configuration file.

## Basics

### Point to MySQL or Postgres

Directly below the `[[database]]` line, add the following options (and modify accordingly for
your MySQL setup):

    host=localhost
    port=3306
    engine=mysql
    user=hue
    password=secretpassword
    name=hue

And run the table creation one time:

    ./build/env/bin/hue migrate

### Specifying the HTTP port

Hue uses CherryPy web server.  You can use the following options to
change the IP address and port that the web server listens on.
The default setting is port 8888 on all configured IP addresses.

    # Webserver listens on this address and port
    http_host=0.0.0.0
    http_port=8888

[Gunicorn](https://gunicorn.org/) support is planned to come in via [HUE-8739](https://issues.cloudera.org/browse/HUE-8739).

### Specifying the Secret Key

For security, you should also specify the secret key that is used for secure
hashing in the session store. Enter a long series of random characters
(30 to 60 characters is recommended).

    secret_key=jFE93j;2[290-eiw.KEiwN2s3['d;/.q[eIW^y#e=+Iei*@Mn<qW5o

NOTE: If you don't specify a secret key, your session cookies will not be
secure. Hue will run but it will also display error messages telling you to
set the secret key.

### Disabling some apps

In the Hue ini configuration file, in the [desktop] section, you can enter the names of the app to hide:

    [desktop]
    # Comma separated list of apps to not load at server startup.
    app_blacklist=beeswax,impala,security,filebrowser,jobbrowser,rdbms,jobsub,pig,hbase,sqoop,zookeeper,metastore,spark,oozie,indexer

[Read more about it here](http://gethue.com/mini-how-to-disabling-some-apps-from-showing-up/).

## Authentication

By default (`AllowFirstUserDjangoBackend`), the first user who logs in to Hue can choose any
username and password and becomes an administrator automatically. This
user can create other user and administrator accounts. User information is
stored in the Django database in the Django backend.

The authentication system is pluggable. Here is a list of some of the possible authentications:

### Username / Password

This is the default Hue backend. It creates the first user that logs in as the super user. After this, it relies on Django and the user manager to authenticate users.

    desktop.auth.backend.AllowFirstUserDjangoBackend

### Allow All

This backend does not require a password for users to log in. All users are automatically authenticated and the username is set to what is provided.

    desktop.auth.backend.AllowAllBackend

### LDAP

Authenticates users against an LDAP service.

    desktop.auth.backend.LdapBackend

There are two ways to bind Hue with an LDAP directory service:

* Search Bind: Hue searches for user credentials with search base (and attribute and filter).
* Direct Bind: Hue authenticates (without searching) in one of two ways:
  * NT Domain: Bind to Microsoft Active Directory with username@domain (the UPN)or
  * Username Pattern: Bind to open standard LDAP with full path of directory information tree (DIT).

Note: Username pattern does not work with AD because AD inserts spaces into the UID which Hue cannot process.

Encryption: To prevent credentials from transmitting in the clear, encrypt with LDAP over SSL, using the LDAPS protocol on the LDAPS port (636 by default); or encrypt with the StartTLS extension using the standard LDAP protocol and port (389 by default). Cloudera recommends LDAPS. You must have a CA Certificate in either case.

Hue Supported LDAP Authentication and Encryption Methods

    LDAP Auth Action	Encrypted (LDAPS)	Encrypted (LDAP+TLS)	Not Encrypted (LDAP)
    Search Bind	AD, LDAP	AD, LDAP	AD, LDAP
    Direct Bind - NT Domain	AD	AD	AD
    Direct Bind - User Pattern	LDAP	LDAP	LDAP

Example of a Search Bind configuration encrypted with LDAPS:

    [[custom]]
    [[auth]]
    backend=desktop.auth.backend.LdapBackend

    [[ldap]]
    ldap_url=ldaps://w2k8-1.ad.sec.cloudera.com:636
    search_bind_authentication=true
    ldap_cert=/<path_to_cacert>/w2k8-1-root.pem
    use_start_tls=false
    create_users_on_login=true
    base_dn="DC=ad,DC=sec,DC=cloudera,DC=com"
    bind_dn="<username>@ad.sec.cloudera.com"
    bind_password_script=<path_to_password_script>/<script.sh>
    test_ldap_user="testuser1"
    test_ldap_group="testgroup1"

    [[[users]]]
    user_filter="objectclass=user"
    user_name_attr="sAMAccountName"

    [[[groups]]]
    group_filter="objectclass=group"
    group_name_attr="cn"
    group_member_attr="member"

Example of a Direct Bind configuration for Active Directory encrypted with LDAPS:

    [[ldap]]
    ldap_url=ldaps://w2k8-1.ad.sec.cloudera.com:636
    search_bind_authentication=false
    nt_domain=ad.sec.cloudera.com
    ldap_cert=/<path_to_cacert>/w2k8-1-root.pem
    use_start_tls=false
    create_users_on_login=true
    base_dn="DC=ad,DC=sec,DC=cloudera,DC=com"
    bind_dn="<username>"
    bind_password_script=<path_to_password_script>/<script.sh>
    ...

Example of a Direct Bind configuration for Active Directory encrypted with StartTLS:

    [[ldap]]
    ldap_url=ldap://w2k8-1.ad.sec.cloudera.com:389
    search_bind_authentication=false
    nt_domain=ad.sec.cloudera.com
    ldap_cert=/opt/cloudera/security/cacerts/w2k8-1-root.pem
    use_start_tls=true
    create_users_on_login=true
    base_dn="DC=ad,DC=sec,DC=cloudera,DC=com"
    bind_dn="cconner"
    bind_password_script=<path_to_password_script>/<script.sh>
    ...


#### Search Bind

Search bind authentication does an ldapsearch against one or more directory services and binds with the found distinguished name (DN) and password. Hue searches the subtree from the base distinguished name. If LDAP Username Attribute is set, Hue looks for an entry whose attribute has the same value as the short name given at login.

Important: Search binding works with all directory service types. It is also the only method that allows synchronizing groups at login (set with sync_groups_on_login in a safety-valve).

Set the following required properties:

Authentication Backend	desktop.auth.backend.LdapBackend

    LDAP URL	ldaps://<ldap_server>:636 (or ldap://<ldap_server>:389)
    LDAP Server CA Certificate	/path_to_certificate/cert.pem
    LDAP Search Base	DC=mycompany,DC=com
    LDAP Bind User Distinguished Name	username@domain
    LDAP Bind Password	bind_user_password
    Use Search Bind Authentication	TRUE
    Enable LDAP TLS	FALSE if using LDAPS or not encrypting
    Create LDAP users on login	TRUE

Note: To encrypt with TLS, set LDAP URL to ldap://<ldap_server>:389 and check Enable LDAP TLS. For a proof of concept without encryption, use ldap://<ldap_server>:389, remove the value for LDAP Server CA Certificate, and uncheck Enable LDAP TLS.

You can optionally improve search performance with attributes and filters.

    LDAP User Filter	objectclass=user (default = *)
    LDAP Username Attribute	sAMAccountName (AD default), uid (LDAP default)
    LDAP Group Filter	objectclass=group (default = *)
    LDAP Group Name Attribute	cn (default)
    LDAP Group Membership Attribute	member (default)

Note: With the user settings in the table above, the LDAP search filter has the form: (&(objectClass=user)(sAMAccountName=<user entered username>)).

Add any valid user and/or valid group to quickly test your LDAP configuration.

    LDAP Username for Test LDAP Configuration	Any valid user
    LDAP Group Name for Test LDAP Configuration	Any valid group

Note: The syntax of Bind Distinguished Name differs per bind method:

    Search Bind: username@domain
    Direct Bind with NT Domain: username
    Direct Bind with Username Pattern: DN string (full DIT path)

Do not use if anonymous binding is supported.

    ## You can test ldapsearch at the command line as follows:
    LDAPTLS_CACERT=/<path_to_cert>/<ca_certificate> ldapsearch -H ldaps://<ldap_server>:636 \
    -D "<bind_dn>" -w <bind_password> -b <base_dn> "samaccountname=<user>"

Note: To run ldapsearch with a CA certificate, you may need to install ldap_utils on Debian/Ubuntu and openldap-clients on RHEL/CentOS.

#### Direct Bind

To authenticate with direct binding, Hue needs either the User Principal Name (UPN) for Active Directory, or the full path to the LDAP user in the Directory Information Tree (DIT) for open standard LDAP.

Important: Direct binding only works with one domain. For multiple directories, use Search Bind.

To directly bind to an Active Directory/LDAP server with NT domain:

Click the Configuration tab and filter by scope=Service-wide and category=Security.

Set LDAP properties exactly like Search Bind with these exceptions:
    Active Directory Domain	<your NT domain>
    LDAP Bind User Distinguished Name	<username only> (not username@domain)
    Use Search Bind Authentication	FALSE

Test your LDAP configuration, and when successful, Restart Hue.
To directly bind to an open standard LDAP server with a username pattern:

Remove the value for Active Directory Domain.

Set both LDAP Username Pattern and LDAP Bind User Distinguished Name to a DN string that represents the full path of the directory information tree, from UID to top level domain.

Note: When using direct bind, set LDAP Search Base, not for authentication (you can log on to Hue without it), but to Synchronize Hue with LDAP Server.

#### Troubleshooting

##### Issue: 
Hue is not able to sync the LDAP group in Hue and it reports the following error : Could not get LDAP details for groups in pattern <group_name>

##### Solution: 
check your configuration if 'subgroups' is set under [[ldap]] and remove it.


### SAML

Secure Assertion Markup Language (SAML) single sign-on (SSO) backend. Delegates authentication to the configured Identity Provider. See Configuring Hue for SAML for more details.

    libsaml.backend.SAML2Backend


Authenticate Hue Users with SAML

Hue supports SAML (Security Assertion Markup Language) for Single Sign-on (SSO) authentication.

The SAML 2.0 Web Browser SSO profile has three components:

* User Agent - Browser that represents you, the user, seeking resources.
* Service Provider (SP) - Service (Hue) that sends authentication requests to SAML.
* Identity Provider (IdP) - SAML service that authenticates users.

When a user requests access to an application, the Service Provider (Hue) sends an authentication request from the User Agent (browser) to the Identity Provider. The Identity Provider authenticates the user, sends a response, and redirects the browser back to Hue.
This page explains how to configure Hue, the Service Provider, and gives guidance on how to configure the Identity Provider, which differs per product.

Configure Hue for SAML Authentication

The Service Provider (Hue) and the Identity Provider use a metadata file to confirm each other's identity. Hue stores metadata from the SAML server, and the IdP stores metadata from Hue server.

In Configure Hue at the Command Line, you must copy the metadata from your IdP's SAML server and store it in an XML file on every ost with a Hue server.
Important: Read the documentation of your Identity Provider for details on how to procure the XML of the SAML server metadata.

Configure Hue at the Command Line
Important: You may need to disable cipher algorithms. See SAML SSL Error in Troubleshooting below.

Install the following libraries on all hosts in your cluster:

    ## RHEL/CentOS
    yum install git gcc python-devel swig openssl
    ## Ubuntu/Debian
    apt-get install git gcc python-dev swig openssl
    ## SLES
    zypper install git gcc python-devel swig openssl make libxslt-devel libltdl-devel

Install xmlsec1 and xmlsec1-openssl on all hosts in the cluster:

Important: Ensure that the xmlsec1 package is executable by the user, hue.

    ## RHEL/CentOS
    yum install xmlsec1 xmlsec1-openssl
    Note: If xmlsec libraries are not available, use the appropriate epel repository:
    ## For RHEL/CentOS 7
    wget http://dl.fedoraproject.org/pub/epel/7/x86_64/e/epel-release-7-6.noarch.rpm
    rpm -ivh epel-release-7-6.noarch.rpm
    ## Ubuntu/Debian
    apt-get install xmlsec1 libxmlsec1-openssl
    ## SLES (get latest version)
    wget http://www.aleksey.com/xmlsec/download/xmlsec1-1.2.24.tar.gz
    tar -xvzf xmlsec1-1.2.24.tar.gz
    cd xmlsec1-1.2.24
    ./configure && make
    make install

Copy metadata from your IdP's SAML server and save it as an XML file on every host with a Hue server.
For example, if your Identity Provider is Shibboleth, visit https://<idp_host>:8443/idp/shibboleth, copy the metadata content, and paste it into an .xml file.

Note: You may have to edit the copied metadata; for example, the IdP's port number (8443) may be missing from its URL.

    mkdir -pm 755 /opt/cloudera/security/saml/
    cd /opt/cloudera/security/saml/
    vim idp-<your idp provider>-metadata.xml

Add key_file and cert_file for encrypted assertions–see Table of SAML Parameters.

Warning: Add key and cert files even if not encrypting assertions. Hue checks for the existence and validity of these files even if they are not needed! They cannot be empty files. This is a known issue.

If necessary, create "valid" dummy files:

    openssl genrsa -des3 -out dummy.key 2048
    openssl rsa -inform PEM -outform PEM -in dummy.key -pubout -out dummy-nopass.pem

Configure Hue

Currently, all hue.ini properties for SAML must be added to Hue Service safety-valve in Cloudera Manager.
Log on to Cloudera Manager and go to Hue > Configuration.

    ## Example Settings using Open AM:
    [desktop]
    redirect_whitelist="^\/.*$,^http:\/\/clr.sec.cloudera.com:8080\/.*$"
    [[auth]]
    backend=libsaml.backend.SAML2Backend
    [libsaml]
    xmlsec_binary=/usr/bin/xmlsec1
    metadata_file=/opt/cloudera/security/saml/idp-openam-metadata.xml
    key_file=/opt/cloudera/security/saml/host.key
    cert_file=/opt/cloudera/security/saml/host.pem
    username_source=nameid
    name_id_format="urn:oasis:names:tc:SAML:2.0:nameid-format:transient"
    entity_id=<host base name>
    logout_enabled=false

Note: For SLES distributions, the xmlsec binary may be in /usr/local/bin/. If so:

* Set Hue Service Advanced Configuration Snippet: xmlsec_binary=/usr/local/bin/xmlsec1
* Set Hue Service Environment Advanced Configuration Snippet: LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib/

Integrate IdP SAML Server with Hue

After Hue is configured and restarted, copy the metadata generated by Hue server and send it to your Identity Provider so they can configure the SAML server.

Ensure Hue is configured, restarted, and running.
Go to http://<hue_fqdn>:8889/saml2/metadata.

Copy the metadata and send it to your Identity Provider.

Ensure that your Identity Provider configures the SAML server with the Hue metadata (just as you configured the Hue server with SAML metadata).

SAML Properties in hue.ini

Table of SAML Parameters

SAML Parameter	Description
    authn_requests_signed	Boolean, that when True, signs Hue-initiated authentication requests with X.509 certificate.
    backend	Hard-coded value set to SAML backend library packaged with Hue (libsaml.backend.SAML2Backend).
    base_url	URL that SAML Identity Provider uses for responses. Typically used in Load balanced Hue environments.
    cert_file	Path to X.509 certificate sent with encrypted metadata. File format must be .PEM.
    create_users_on_login	Boolean, that when True, creates users from OpenId, upon successful login.
    entity_id	Service provider ID. Can also accept pattern where '<base_url>' is replaced with server URL base.
    key_file	Path to private key used to encrypt metadata. File format must be .PEM.
    key_file_password	Password used to decrypt the X.509 certificate in memory.
    logout_enabled	Boolean, that when True, enables single logout.
    logout_requests_signed	Boolean, that when True, signs Hue-initiated logout requests with an X.509 certificate.
    metadata_file	Path to readable metadata XML file copied from Identity Provider.
    name_id_format	Format of NameID that Hue requests from SAML server.
    optional_attributes	Comma-separated list of optional attributes that Hue requests from Identity Provider.
    required_attributes	Comma-separated list of required attributes that Hue requests from Identity Provider. For example, uid and email.
    redirect_whitelist	Fully qualified domain name of SAML server: "^\/.*$,^https:\/\/<SAML_server_FQDN>\/.*$".
    user_attribute_mapping	Map of Identity Provider attributes to Hue django user attributes. For example, {'uid':'username', 'email':'email'}.
    username_source	Declares source of username as nameid or attributes.
    xmlsec_binary	Path to xmlsec_binary that signs, verifies, encrypts/decrypts SAML requests and assertions. Must be executable by user, hue.
    Description of some properties to be set in hue.ini (via Cloudera Manager):
    redirect_whitelist [desktop]

Set to the fully qualified domain name of the SAML server so that Hue can redirect to the SAML server for authentication.

    [desktop]
    redirect_whitelist=^\/.$,^https:\/\/<SAML_server_fully_qualified_domain_name>\/.$
    Note: Hue uses redirect_whitelist to protect itself from redirecting to unapproved URLs.
    backend [desktop]>[[auth]]
    Point to the SAML backend (packaged with Hue):
    backend=libsaml.backend.SAML2Backend
    xmlsec_binary [libsaml]
    Point to the xmlsec1 library path:
    xmlsec_binary=/usr/bin/xmlsec1
    Note: To find the path, run: which xmlsec1
    metadata_file [libsaml]
    Point to the path of the XML file you created from the IdP's metadata:
    metadata_file=/path/to/<your_idp_metadata_file>.xml
    key_file and cert_file [libsaml]

To encrypt communication between Hue and the Identity Provider, you need a private key and certificate. The private key signs requests sent to the Identity Provider and the certificate file encrypts and decrypts messages from the Identity Provider.

Copy these files from the Identity Provider and set key_file and cert_file to their respective paths. Both files are in PEM format and must be named with the .PEM extension.

Note: The key and certificate files specified by the key_file and cert_file parameters in hue.ini must be .PEM files.
Users with password-protected certificates can set the property, key_file_password in hue.ini. Hue uses the password to decrypt the SAML certificate in memory and passes it to xmlsec1 through a named pipe. The decrypted certificate never touches the disk. This only works for POSIX-compatible platforms.

Troubleshooting

Remember to Enable DEBUG for logging.

SAML SSL Error

OpenSSL might fail in CDH 5.5.x and higher with this message:

    SSLError: [Errno bad handshake] [('SSL routines', 'SSL3_CHECK_CERT_AND_ALGORITHM', 'dh key too small')]

To resolve, append the following code to the file, /usr/java/<your_jdk_version>-cloudera/jre/lib/security/java.security:

    jdk.tls.disabledAlgorithms=MD5, RC4, DH

SAML Decrypt Error

The following error is an indication that you are using a slightly different SAML protocol from what Hue expects:

    Error: ('failed to decrypt', -1)

To resolve:

Download and rename Python script, fix-xmlsec1.txt.

    wget http://www.cloudera.com/documentation/other/shared/fix-xmlsec1.txt -O fix-xmlsec1.py

Change permissions as appropriate, for example:

    chmod 755 fix-xmlsec1.py

In hue.ini, set xmlsec_binary=<path_to_script>/fix-xmlsec1.py.
Run fix-xmlsec1.py.

This script repairs the known issue whereby xmlsec1 is not compiled with RetrievalMethod and cannot find the location of the encrypted key. SAML2 responses would sometimes place EncryptedKey outside of the EncryptedData tree. This script moves EncryptedKey under EncryptedData.


### Spnego

SPNEGO is an authentication mechanism negotiation protocol. Authentication can be delegated to an authentication server, such as a Kerberos KDC, depending on the mechanism negotiated.

    desktop.auth.backend.SpnegoDjangoBackend

### PAM

Authenticates users with PAM (pluggable authentication module). The authentication mode depends on the PAM module used.

    desktop.auth.backend.PamBackend

### OAuth Connect

Delegates authentication to a third-party OAuth server.

    desktop.auth.backend.OAuthBackend

### Multiple Authentication Backends

For example, to enable Hue to first attempt LDAP directory lookup before falling back to the database-backed user model, we can update the hue.ini configuration file or Hue safety valve in Cloudera Manager with a list containing first the LdapBackend followed by either the ModelBackend or custom AllowFirstUserDjangoBackend (permits first login and relies on user model for all subsequent authentication):

    [desktop]
      [[auth]]
      backend=desktop.auth.backend.LdapBackend,desktop.auth.backend.AllowFirstUserDjangoBackend

This tells Hue to first check against the configured LDAP directory service, and if the username is not found in the directory, then attempt to authenticate the user with the Django user manager.

[Read more about it here](http://gethue.com/configuring-hue-multiple-authentication-backends-and-ldap/).

## Security

### Configure a Proxy

We explained how to run Hue with NGINX serving the static files or under Apache. If you use another proxy, you might need to set these options:

<pre>
  [desktop]
  # Enable X-Forwarded-Host header if the load balancer requires it.
  use_x_forwarded_host=false

  # Support for HTTPS termination at the load-balancer level with SECURE_PROXY_SSL_HEADER.
  secure_proxy_ssl_header=false
</pre>

### Configuring SSL

You can configure Hue to serve over HTTPS.

1. Configure Hue to use your private key by adding the following
options to the `hue.ini` configuration file:

    ssl_certificate=/path/to/certificate
    ssl_private_key=/path/to/key

2. Ideally, you would have an appropriate key signed by a Certificate Authority.
If you're just testing, you can create a self-signed key using the `openssl`
command that may be installed on your system:

Create a key:

    openssl genrsa 1024 > host.key

Create a self-signed certificate:

    openssl req -new -x509 -nodes -sha1 -key host.key > host.cert


<div class="note">
Self-signed Certificates and File Uploads

To upload files using the Hue File Browser over HTTPS requires
using a proper SSL Certificate.  Self-signed certificates don't
work.
</div>

Note: The security vulnerability SWEET32 is also called Birthday attacks against TLS ciphers with 64bit block size and it is assigned CVE-2016-2183. This is due to legacy block ciphers
having block size of 64 bits are vulnerable to a practical collision attack when used in CBC mode.

DES/3DES are the only ciphers has block size of 64-bit. One way to config Hue not to use them:

    [desktop]
    ssl_cipher_list=DEFAULT:!DES:!3DES

### SASL

When getting a bigger result set from Hive/Impala or bigger files like images from HBase, the response requires to increase
the buffer size of SASL lib for thrift sasl communication.

<pre>
  [desktop]
  # This property specifies the maximum size of the receive buffer in bytes in thrift sasl communication,
  # default value is 2097152 (2 MB), which equals to (2 * 1024 * 1024)
  sasl_max_buffer=2097152
</pre>

### Storing passwords in file script

Hue lets you secure passwords in one consolidated script, or multiple individual scripts. Hue runs each password script at startup and extracts passwords from stdout.

Store scripts in a directory that only Hue can read, write, and execute. You can choose password script names but you cannot change hue.ini property names to which you assign those scripts.

At the command line, create one or more password scripts. For example, create a consolidated script named `my_passwords_script.sh`:

    #!/bin/bash

    SERVICE=$1

    if [[ ${SERVICE} == "ldap_password" ]]
    then
    echo "your_ldap_password"
    fi

    if [[ ${SERVICE} == "ssl_password" ]]
    then
    echo "your_ssl_password"
    fi

    if [[ ${SERVICE} == "bind_password" ]]
    then
    echo "your_bind_password"
    fi

    if [[ ${SERVICE} == "db_password" ]]
    then
    echo "your_database_password"
    fi

Add script properties, for example:

    [desktop]
    ldap_username=hueservice
    ldap_password_script="/var/lib/hue/password_script.sh ldap_password"
    ssl_password_script="/var/lib/hue/password_script.sh ssl_password"

    [[ldap]]
    bind_password_script="/var/lib/hue/password_script.sh bind_password"

    [[database]]
    db_password_script="/var/lib/hue/password_script.sh db_password"


### Idle session timeout

Hue now offers a new property, idle_session_timeout, that can be configured in the hue.ini file:

    [desktop]
    [[auth]]
    idle_session_timeout=600

When idle_session_timeout is set, users will automatically be logged out after N (e.g. – 600) seconds of inactivity and be prompted to login again:

[Read more about it here](http://gethue.com/introducing-the-new-login-modal-and-idle-session-timeout/).

### Auditing

Read more about [Auditing User Administration Operations with Hue and Cloudera Navigator](http://gethue.com/auditing-user-administration-operations-with-hue-and-cloudera-navigator-2/).

### Concurrent User Session Limit

If set, limits the number of concurrent user sessions. 1 represents 1 browser session per user. Default: 0 (unlimited sessions per user)

    [desktop]
    [[session]]
    concurrent_user_session_limit=0

[Read more about it here](http://gethue.com/restrict-number-of-concurrent-sessions-per-user/).

## Customize the UI

### Maps look and feel

The properties we need to tweak are leaflet_tile_layer and leaflet_tile_layer_attribution, that can be configured in the hue.ini file:

    [desktop]
    leaflet_tile_layer=https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}
    leaflet_tile_layer_attribution='Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'

[Read more about it here](http://gethue.com/change-your-maps-look-and-feel/).

### Banner
You can add a custom banner to the Hue Web UI by applying HTML directly to the property, banner_top_html. For example:

    banner_top_html=<H4>My company's custom Hue Web UI banner</H4>

### Splash Screen
You can customize a splash screen on the login page by applying HTML directly to the property, login_splash_html. For example:

    [desktop]
    [[custom]]
    login_splash_html=WARNING: You are required to have authorization before you proceed.

### Custom Logo

There is also the possibility to change the logo for further personalization.

    [desktop]
    [[custom]]
    # SVG code to replace the default Hue logo in the top bar and sign in screen
    # e.g. <image xlink:href="/static/desktop/art/hue-logo-mini-white.png" x="0" y="0" height="40" width="160" />
    logo_svg=

You can go crazy and write there any SVG code you want. Please keep in mind your SVG should be designed to fit in a 160×40 pixels space. To have the same ‘hearts logo' you can see above, you can type this code

    [desktop]
    [[custom]]
    logo_svg='<g><path stroke="null" id="svg_1" d="m44.41215,11.43463c-4.05017,-10.71473 -17.19753,-5.90773 -18.41353,-0.5567c-1.672,-5.70253 -14.497,-9.95663 -18.411,0.5643c-4.35797,11.71793 16.891,22.23443 18.41163,23.95773c1.5181,-1.36927 22.7696,-12.43803 18.4129,-23.96533z" fill="#ffffff"/> <path stroke="null" id="svg_2" d="m98.41246,10.43463c-4.05016,-10.71473 -17.19753,-5.90773 -18.41353,-0.5567c-1.672,-5.70253 -14.497,-9.95663 -18.411,0.5643c-4.35796,11.71793 16.891,22.23443 18.41164,23.95773c1.5181,-1.36927 22.76959,-12.43803 18.41289,-23.96533z" fill="#FF5A79"/> <path stroke="null" id="svg_3" d="m154.41215,11.43463c-4.05016,-10.71473 -17.19753,-5.90773 -18.41353,-0.5567c-1.672,-5.70253 -14.497,-9.95663 -18.411,0.5643c-4.35796,11.71793 16.891,22.23443 18.41164,23.95773c1.5181,-1.36927 22.76959,-12.43803 18.41289,-23.96533z" fill="#ffffff"/> </g>'

Read more about it in [Hue with a custom logo](http://gethue.com/hue-with-a-custom-logo/) post.

## Source Version Control

By default Hue stores the [saved documents]({{% param baseURL %}}user/concept/#documents) in its database. This features aims at pointing to any source versioning systems like GitHub, BitBucket... to open and save queries.

**Note** This feature is experiemental and tracked in [HUE-951](https://issues.cloudera.org/browse/HUE-951).

    [desktop]

    [[vcs]]

    ## [[[git-read-only]]]
        ## Base URL to Remote Server
        # remote_url=https://github.com/cloudera/hue/tree/master

        ## Base URL to Version Control API
        # api_url=https://api.github.com
    ## [[[github]]]

        ## Base URL to Remote Server
        # remote_url=https://github.com/cloudera/hue/tree/master

        ## Base URL to Version Control API
        # api_url=https://api.github.com

        # These will be necessary when you want to write back to the repository.
        ## Client ID for Authorized Application
        # client_id=

        ## Client Secret for Authorized Application
        # client_secret=
    ## [[[svn]]
        ## Base URL to Remote Server
        # remote_url=https://github.com/cloudera/hue/tree/master

        ## Base URL to Version Control API
        # api_url=https://api.github.com

        # These will be necessary when you want to write back to the repository.
        ## Client ID for Authorized Application
        # client_id=

        ## Client Secret for Authorized Application
        # client_secret=
