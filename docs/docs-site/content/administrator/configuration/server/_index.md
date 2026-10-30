---
title: "Server"
date: 2019-03-13T18:28:09-07:00
draft: false
weight: 1
---

This page explains how to configure the Hue server itself.
Unless stated otherwise, the properties below go under the `[desktop]` section of the `hue.ini` file.

## Basics

### Point to MySQL or PostgreSQL

Hue stores users and saved queries in a database. To use MySQL or PostgreSQL instead of the default SQLite, add the following options directly below the `[[database]]` line (under `[desktop]`). Change them to match your setup:

```ini
[desktop]
  [[database]]
    host=localhost
    port=3306
    engine=mysql
    user=hue
    password=secretpassword
    name=hue
```

For PostgreSQL, set `engine=postgresql_psycopg2` and use your PostgreSQL port.
For MariaDB, use the `mysql` engine.

Then create the tables. You only need to do this once:

```bash
./build/env/bin/hue migrate
```

See [Configuring with another database](/administrator/administration/database/#configure-another-database) for the full steps, including how to migrate existing data.

### Specify the HTTP port

Use the following options to change the IP address and port that the web server listens on.
The default is port 8888 on all configured IP addresses.

```ini
[desktop]
  # Webserver listens on this address and port
  http_host=0.0.0.0
  http_port=8888
```

### Gunicorn server

Hue serves requests with [Gunicorn](https://gunicorn.org/) by default. You can tune it with these options:

```ini
[desktop]
  # Gunicorn worker class: gevent, eventlet, gthread or sync.
  gunicorn_work_class=gthread

  # Number of Gunicorn worker processes.
  gunicorn_number_of_workers=1

  # Workers silent for more than this many seconds are killed and restarted.
  gunicorn_worker_timeout=900

  # After a restart signal, workers have this many seconds to finish their requests.
  gunicorn_worker_graceful_timeout=900
```

> **Note**: `use_cherrypy_server` is still a valid option, but CherryPy is no longer part of the Hue Python requirements. On Python 3 the default is `false`: keep it and use Gunicorn.

### Specify the secret key

Set a secret key to protect the hashing of the session store. Use a long series of random characters (30 to 60 characters is recommended).

```ini
[desktop]
  secret_key=jFE93j;2[290-eiw.KEiwN2s3['d;/.q[eIW^y#e=+Iei*@Mn<qW5o
```

You can also generate the key with a script by setting `secret_key_script`, or by setting the `HUE_SECRET_KEY` environment variable.

> **Note**: If you don't set a secret key, your session cookies are not secure. Hue runs, but it displays error messages telling you to set the key.

### Disable some apps

To hide apps, list their names in `app_blacklist`:

```ini
[desktop]
  # Comma separated list of apps to not load at server startup.
  app_blacklist=pig,hbase,sqoop,zookeeper,oozie
```

[Read more about it here](http://gethue.com/mini-how-to-disabling-some-apps-from-showing-up/).

## Authentication

By default, Hue uses the `AllowFirstUserDjangoBackend` backend. The first user who logs in can choose any username and password and becomes an administrator automatically. This user can create other users and administrators. Hue stores user information in its database.

The authentication system is pluggable. You select one or more backends with the `backend` property in the `[[auth]]` section. These are the main options.

### Username and password

This is the default Hue backend. It makes the first user who logs in the superuser. After that, it relies on Django and the user manager to authenticate users.

```ini
[desktop]
  [[auth]]
    backend=desktop.auth.backend.AllowFirstUserDjangoBackend
```

### Allow all

This backend does not require a password. Hue authenticates every user automatically and uses the username that is provided.

```ini
[desktop]
  [[auth]]
    backend=desktop.auth.backend.AllowAllBackend
```

> **Warning**: Do not use this backend on a server that others can reach.

### LDAP

This backend authenticates users against an LDAP service.

```ini
[desktop]
  [[auth]]
    backend=desktop.auth.backend.LdapBackend
```

There are two ways to bind Hue to an LDAP directory service:

* Search bind: Hue searches for the user with a search base (and optionally an attribute and a filter), then binds with the DN it found.
* Direct bind: Hue authenticates without searching, in one of two ways:
  * NT domain: bind to Microsoft Active Directory with `username@domain` (the UPN).
  * Username pattern: bind to an open standard LDAP server with the full path in the directory information tree (DIT).

> **Note**: The username pattern does not work with Active Directory (AD), because AD inserts spaces into the UID, which Hue cannot process.

To avoid sending credentials in the clear, encrypt the connection. Use LDAP over SSL (LDAPS) on port 636 by default, or the StartTLS extension on the standard LDAP port (389 by default). LDAPS is recommended. In both cases you need a CA certificate.

The following table lists the supported combinations of authentication method and encryption.

| LDAP auth action           | Encrypted (LDAPS) | Encrypted (LDAP+TLS) | Not encrypted (LDAP) |
| -------------------------- | ----------------- | -------------------- | -------------------- |
| Search bind                | AD, LDAP          | AD, LDAP             | AD, LDAP             |
| Direct bind - NT domain    | AD                | AD                   | AD                   |
| Direct bind - user pattern | LDAP              | LDAP                 | LDAP                 |

#### Search bind

Search bind does an `ldapsearch` against one or more directory services and binds with the DN it finds and the user's password. Hue searches the subtree below the base DN. If `user_name_attr` is set, Hue looks for an entry whose attribute has the same value as the short name entered at login.

> **Note**: Search bind works with all directory service types. It is also the only method that can synchronize groups at login (set `sync_groups_on_login`).

Example of a search bind configuration encrypted with LDAPS:

```ini
[desktop]
  [[auth]]
    backend=desktop.auth.backend.LdapBackend

  [[ldap]]
    ldap_url=ldaps://ldap.example.com:636
    search_bind_authentication=true
    ldap_cert=/<path_to_cacert>/ca-root.pem
    use_start_tls=false
    create_users_on_login=true
    base_dn="DC=ad,DC=example,DC=com"
    bind_dn="<username>@ad.example.com"
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
```

The main properties are:

| Property                     | Value                                                                  |
| ---------------------------- | ---------------------------------------------------------------------- |
| `ldap_url`                   | `ldaps://<ldap_server>:636` (or `ldap://<ldap_server>:389`)            |
| `ldap_cert`                  | Path to the CA certificate of the LDAP server, for example `/path_to_certificate/cert.pem` |
| `base_dn`                    | The search base, for example `DC=mycompany,DC=com`                     |
| `bind_dn`                    | The bind user, in the form `username@domain`                           |
| `bind_password_script`       | Script that prints the bind user password (see [Store passwords in a script](#store-passwords-in-a-script)) |
| `search_bind_authentication` | `true`                                                                 |
| `use_start_tls`              | `false` for LDAPS or no encryption, `true` for StartTLS                |
| `create_users_on_login`      | `true`                                                                 |

> **Note**: To encrypt with StartTLS, set `ldap_url` to `ldap://<ldap_server>:389` and `use_start_tls=true`. For a proof of concept without encryption, use `ldap://<ldap_server>:389`, remove `ldap_cert`, and set `use_start_tls=false`.

You can optionally improve the search performance with filters and attributes:

| Property            | Value                                                      |
| ------------------- | ---------------------------------------------------------- |
| `user_filter`       | For example `objectclass=user`                             |
| `user_name_attr`    | `sAMAccountName` for AD, `uid` for most other LDAP servers |
| `group_filter`      | For example `objectclass=group`                            |
| `group_name_attr`   | `cn`                                                       |
| `group_member_attr` | `member`                                                   |

> **Note**: With these user settings, the LDAP search filter looks like `(&(objectClass=user)(sAMAccountName=<username entered at login>))`.

To test your configuration, set `test_ldap_user` and `test_ldap_group` to a valid user and a valid group.

> **Note**: The syntax of `bind_dn` depends on the bind method.
>
> * Search bind: `username@domain`
> * Direct bind with NT domain: `username`
> * Direct bind with username pattern: a DN string (the full DIT path)

Skip `bind_dn` and `bind_password_script` if your server supports anonymous binding.

You can test your settings with `ldapsearch` on the command line:

```bash
LDAPTLS_CACERT=/<path_to_cert>/<ca_certificate> ldapsearch -H ldaps://<ldap_server>:636 \
  -D "<bind_dn>" -w <bind_password> -b <base_dn> "samaccountname=<user>"
```

> **Note**: To run `ldapsearch` with a CA certificate, you might need to install `ldap-utils` on Debian/Ubuntu or `openldap-clients` on RHEL/CentOS.

#### Direct bind

For direct bind, Hue needs either the user principal name (UPN) for Active Directory, or the full path to the LDAP user in the DIT for open standard LDAP.

> **Note**: Direct bind only works with one domain. For multiple directories, use search bind.

To bind directly to an Active Directory server with an NT domain, configure the properties like a search bind, with these changes:

* Set `nt_domain` to your NT domain.
* Set `bind_dn` to the username only (not `username@domain`).
* Set `search_bind_authentication=false`.

```ini
[desktop]
  [[ldap]]
    ldap_url=ldaps://ldap.example.com:636
    search_bind_authentication=false
    nt_domain=ad.example.com
    ldap_cert=/<path_to_cacert>/ca-root.pem
    use_start_tls=false
    create_users_on_login=true
    base_dn="DC=ad,DC=example,DC=com"
    bind_dn="<username>"
    bind_password_script=<path_to_password_script>/<script.sh>
```

To use StartTLS instead of LDAPS, set `ldap_url=ldap://ldap.example.com:389` and `use_start_tls=true`.

To bind directly to an open standard LDAP server with a username pattern:

* Leave `nt_domain` empty.
* Set `ldap_username_pattern` to a DN string that represents the full path in the DIT, from the UID up to the top-level domain.
* Set `bind_dn` to a DN string in the same format.

> **Note**: With direct bind, set `base_dn` anyway. You can log in to Hue without it, but you need it to synchronize Hue with the LDAP server.

Test your LDAP configuration, then restart Hue.

#### Troubleshooting LDAP

**Issue**: Hue cannot synchronize an LDAP group and reports `Could not get LDAP details for groups in pattern <group_name>`.

**Solution**: Check your configuration. If `subgroups` is set under `[[ldap]]`, remove it.

### SAML

The Security Assertion Markup Language (SAML) single sign-on (SSO) backend delegates authentication to the Identity Provider you configure.

```ini
[desktop]
  [[auth]]
    backend=libsaml.backend.SAML2Backend
```

The SAML 2.0 Web Browser SSO profile has three components:

* User Agent: the browser that represents you, the user, requesting resources.
* Service Provider (SP): the service (Hue) that sends authentication requests to SAML.
* Identity Provider (IdP): the SAML service that authenticates users.

When a user requests access to an application, the Service Provider (Hue) sends an authentication request from the User Agent (browser) to the Identity Provider. The Identity Provider authenticates the user, sends a response, and redirects the browser back to Hue.

This section explains how to configure Hue as the Service Provider. How you configure the Identity Provider differs per product.

#### Configure Hue for SAML

The Service Provider (Hue) and the Identity Provider use a metadata file to confirm each other's identity. Hue stores the metadata from the SAML server, and the IdP stores the metadata from the Hue server.

1. Install the build libraries on every host that runs a Hue server:

   ```bash
   # RHEL/CentOS
   yum install git gcc python3-devel swig openssl
   # Ubuntu/Debian
   apt-get install git gcc python3-dev swig openssl
   # SLES
   zypper install git gcc python3-devel swig openssl make libxslt-devel libltdl-devel
   ```

2. Install `xmlsec1` on every host that runs a Hue server. Make sure the user that runs Hue can execute it.

   ```bash
   # RHEL/CentOS
   yum install xmlsec1 xmlsec1-openssl
   # Ubuntu/Debian
   apt-get install xmlsec1 libxmlsec1-openssl
   ```

3. Copy the metadata from your IdP's SAML server and save it as an XML file on every host with a Hue server. Read the documentation of your Identity Provider to find how to get this metadata. For example, with Shibboleth, open `https://<idp_host>:8443/idp/shibboleth`, copy the metadata content, and paste it into an `.xml` file.

   > **Note**: You might need to edit the copied metadata. For example, the IdP port number (8443) can be missing from its URL.

   ```bash
   mkdir -pm 755 /path/to/saml/
   cd /path/to/saml/
   vim idp-<your idp provider>-metadata.xml
   ```

4. Set `key_file` and `cert_file` (see the [SAML properties](#saml-properties)).

   > **Warning**: Set the key and certificate files even if you do not encrypt assertions. Hue checks that these files exist and are valid, even when they are not needed. They cannot be empty files. This is a known issue.

   If necessary, create dummy files:

   ```bash
   openssl genrsa -des3 -out dummy.key 2048
   openssl rsa -inform PEM -outform PEM -in dummy.key -pubout -out dummy-nopass.pem
   ```

5. Add the SAML settings to `hue.ini`. Example with OpenAM:

   ```ini
   [desktop]
     redirect_whitelist="^\/.*$,^http:\/\/<saml_server_fqdn>:8080\/.*$"
     [[auth]]
       backend=libsaml.backend.SAML2Backend

   [libsaml]
     xmlsec_binary=/usr/bin/xmlsec1
     metadata_file=/path/to/saml/idp-openam-metadata.xml
     key_file=/path/to/saml/host.key
     cert_file=/path/to/saml/host.pem
     username_source=nameid
     name_id_format="urn:oasis:names:tc:SAML:2.0:nameid-format:transient"
     entity_id=<host base name>
     logout_enabled=false
   ```

   > **Note**: On SLES, the `xmlsec1` binary can be in `/usr/local/bin/`. If so, set `xmlsec_binary=/usr/local/bin/xmlsec1` and add `/usr/local/lib/` to `LD_LIBRARY_PATH` for the Hue process.

6. Restart Hue.

#### Integrate the IdP with Hue

After you configure and restart Hue, send the metadata that Hue generates to your Identity Provider so that they can configure the SAML server.

1. Make sure Hue is configured, restarted, and running.
2. Open `http://<hue_fqdn>:<http_port>/saml2/metadata/` (port 8888 by default).
3. Copy the metadata and send it to your Identity Provider.
4. Make sure your Identity Provider configures the SAML server with the Hue metadata, just as you configured Hue with the SAML server metadata.

#### SAML properties

The following properties go in the `[libsaml]` section unless stated otherwise.

| Property                  | Description                                                                                                                                         |
| ------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| `authn_requests_signed`   | Boolean. When true, signs Hue-initiated authentication requests with an X.509 certificate.                                                           |
| `backend`                 | In `[desktop]` > `[[auth]]`. Set to `libsaml.backend.SAML2Backend`.                                                                                  |
| `base_url`                | URL that the SAML Identity Provider uses for responses. Typically used in load-balanced Hue environments.                                            |
| `cert_file`               | Path to the X.509 certificate sent with the encrypted metadata. The file must be in PEM format.                                                      |
| `create_users_on_login`   | Boolean. When true, creates users on successful login.                                                                                               |
| `entity_id`               | Service provider ID. Accepts a pattern where `<base_url>` is replaced with the server URL base.                                                      |
| `key_file`                | Path to the private key used to encrypt the metadata. The file must be in PEM format.                                                                |
| `key_file_password`       | Password used to decrypt the X.509 certificate in memory. You can use `key_file_password_script` instead.                                           |
| `logout_enabled`          | Boolean. When true, enables single logout.                                                                                                           |
| `logout_requests_signed`  | Boolean. When true, signs Hue-initiated logout requests with an X.509 certificate.                                                                   |
| `metadata_file`           | Path to the readable metadata XML file copied from the Identity Provider.                                                                            |
| `name_id_format`          | Format of the NameID that Hue requests from the SAML server.                                                                                         |
| `optional_attributes`     | Comma-separated list of optional attributes that Hue requests from the Identity Provider.                                                            |
| `required_attributes`     | Comma-separated list of required attributes that Hue requests from the Identity Provider. For example, `uid` and `email`.                           |
| `redirect_whitelist`      | In `[desktop]`. Comma-separated regular expressions of allowed redirect URLs, such as `^\/.*$,^https:\/\/<SAML_server_FQDN>\/.*$`.                   |
| `user_attribute_mapping`  | Map of Identity Provider attributes to Hue Django user attributes. For example, `{'uid':'username', 'email':'email'}`.                              |
| `username_source`         | Source of the username: `nameid` or `attributes`.                                                                                                    |
| `xmlsec_binary`           | Path to the `xmlsec1` binary that signs, verifies, encrypts, and decrypts SAML requests and assertions. The Hue user must be able to execute it. To find the path, run `which xmlsec1`. |

Notes:

* `redirect_whitelist` protects Hue from redirecting to unapproved URLs. Set it so that Hue can redirect to your SAML server for authentication.
* To encrypt communication between Hue and the Identity Provider, you need a private key and a certificate. Both files must be in PEM format.
* If your certificate is password protected, set `key_file_password`. Hue uses it to decrypt the certificate in memory and passes it to `xmlsec1` through a named pipe. The decrypted certificate never touches the disk. This only works on POSIX-compatible platforms.

#### Troubleshooting SAML

Enable `DEBUG` logging first.

**SAML decrypt error**

This error means that your Identity Provider uses a slightly different SAML protocol than Hue expects:

```text
Error: ('failed to decrypt', -1)
```

To resolve it:

1. Download the `fix-xmlsec1.txt` script and rename it:

   ```bash
   wget http://www.cloudera.com/documentation/other/shared/fix-xmlsec1.txt -O fix-xmlsec1.py
   ```

2. Make it executable:

   ```bash
   chmod 755 fix-xmlsec1.py
   ```

3. In `hue.ini`, set `xmlsec_binary=<path_to_script>/fix-xmlsec1.py`.

The script fixes a known issue: `xmlsec1` is not compiled with `RetrievalMethod` and cannot find the encrypted key. SAML2 responses sometimes place `EncryptedKey` outside of the `EncryptedData` tree. The script moves `EncryptedKey` under `EncryptedData`.

### SPNEGO

SPNEGO is an authentication mechanism negotiation protocol. Depending on the negotiated mechanism, authentication can be delegated to an authentication server, such as a Kerberos KDC.

```ini
[desktop]
  [[auth]]
    backend=desktop.auth.backend.SpnegoDjangoBackend
```

### PAM

This backend authenticates users with PAM (pluggable authentication modules). The authentication mode depends on the PAM module you use.

```ini
[desktop]
  [[auth]]
    backend=desktop.auth.backend.PamBackend
```

### OAuth

This backend delegates authentication to a third-party OAuth server.

```ini
[desktop]
  [[auth]]
    backend=desktop.auth.backend.OAuthBackend
```

### Multiple authentication backends

You can list several backends. Hue tries them in order.

For example, to try an LDAP lookup first and fall back to the database-backed user model, list `LdapBackend` first and `AllowFirstUserDjangoBackend` second:

```ini
[desktop]
  [[auth]]
    backend=desktop.auth.backend.LdapBackend,desktop.auth.backend.AllowFirstUserDjangoBackend
```

Hue first checks the configured LDAP directory. If it does not find the username there, it authenticates the user with the Django user manager.

[Read more about it here](http://gethue.com/configuring-hue-multiple-authentication-backends-and-ldap/).

## Security

### Configure a proxy

If you run Hue behind a proxy other than NGINX or Apache, you might need to set these options:

```ini
[desktop]
  # Enable X-Forwarded-Host header if the load balancer requires it.
  use_x_forwarded_host=false

  # Support for HTTPS termination at the load-balancer level with SECURE_PROXY_SSL_HEADER.
  secure_proxy_ssl_header=false
```

### Configure SSL

You can configure Hue to serve over HTTPS.

1. Point Hue to your private key and certificate in `hue.ini`:

   ```ini
   [desktop]
     ssl_certificate=/path/to/certificate
     ssl_private_key=/path/to/key
   ```

2. Use a key signed by a Certificate Authority. For testing only, you can create a self-signed certificate with `openssl`:

   ```bash
   # Create a key
   openssl genrsa 2048 > host.key

   # Create a self-signed certificate
   openssl req -new -x509 -nodes -sha256 -key host.key > host.cert
   ```

> **Note**: To upload files with the File Browser over HTTPS, you need a proper SSL certificate. Self-signed certificates do not work.

> **Note**: The SWEET32 vulnerability (CVE-2016-2183) affects legacy block ciphers with a 64-bit block size, used in CBC mode. DES and 3DES are the only ciphers with a 64-bit block size. To stop Hue from using them:
>
> ```ini
> [desktop]
>   ssl_cipher_list=DEFAULT:!DES:!3DES
> ```

### SASL

Large result sets from Hive or Impala, or large files such as images from HBase, can require a bigger SASL buffer for Thrift SASL communication.

```ini
[desktop]
  # Maximum size of the receive buffer in bytes in Thrift SASL communication.
  # Default is 2097152 (2 MB), which equals 2 * 1024 * 1024.
  sasl_max_buffer=2097152
```

### Store passwords in a script

Hue can read passwords from one consolidated script or from several individual scripts. Hue runs each password script at startup and reads the password from its standard output.

Store the scripts in a directory that only the Hue user can read, write, and execute. You can choose the script names, but you cannot change the `hue.ini` property names that you assign them to.

For example, create a consolidated script named `password_script.sh`:

```bash
#!/bin/bash

SERVICE=$1

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
```

Then reference it in `hue.ini`:

```ini
[desktop]
  ssl_password_script="/var/lib/hue/password_script.sh ssl_password"

  [[ldap]]
    bind_password_script="/var/lib/hue/password_script.sh bind_password"

  [[database]]
    password_script="/var/lib/hue/password_script.sh db_password"
```

### Login and session settings

These properties are in the `[[auth]]` section:

```ini
[desktop]
  [[auth]]
    # Users expire after n seconds without logging in. A negative number means users never expire.
    expires_after=-1

    # Apply 'expires_after' to superusers.
    expire_superusers=true

    # Log users out after n seconds of inactivity. A negative number means idle sessions never time out.
    idle_session_timeout=-1

    # Force users to change their password on first login with desktop.auth.backend.AllowFirstUserDjangoBackend.
    change_default_password=false

    # Number of login attempts allowed before a record is created for failed logins.
    login_failure_limit=3

    # Lock out an IP (and optionally a user agent) after the allowed login attempts are exceeded.
    login_lock_out_at_failure=false

    # Period of inactivity, in hours, after which failed logins are forgotten.
    # A value of 0 or None disables this check.
    login_cooloff_time=None

    # Lock out based on an IP address AND a user agent. Requests from different user agents
    # but from the same IP are then treated differently.
    login_lock_out_use_user_agent=false

    # Lock out based on a combination of user and IP.
    login_lock_out_by_combination_user_and_ip=false
```

When `idle_session_timeout` is set (for example, `idle_session_timeout=600`), users are logged out after that many seconds of inactivity and are prompted to log in again.

[Read more about it here](http://gethue.com/introducing-the-new-login-modal-and-idle-session-timeout/).

### Concurrent user session limit

You can limit the number of concurrent sessions per user. A value of `1` allows one browser session per user. The default is `0` (unlimited).

```ini
[desktop]
  [[session]]
    concurrent_user_session_limit=0
```

[Read more about it here](http://gethue.com/restrict-number-of-concurrent-sessions-per-user/).

## Query execution timeouts

A long SQL query can time out in a proxy with an error like this:

```text
504 Gateway Time-out nginx/1.17.10
```

One solution is to run long, blocking, or resource-intensive operations in tasks outside of the server. This is particularly useful for databases other than Hive or Impala that use the SQLAlchemy interface, which blocks until the query finishes.

Read more in the [Task Server section](/administrator/administration/reference/#task-server) of the reference guide.

Another solution is to increase the NGINX timeouts from 30 seconds to several minutes. For example, with the Kubernetes NGINX ingress:

```yaml
nginx.ingress.kubernetes.io/proxy-connect-timeout: '900'
nginx.ingress.kubernetes.io/proxy-read-timeout: '900'
nginx.ingress.kubernetes.io/proxy-send-timeout: '900'
```

## Customization

### Language

Hue detects the user language automatically. Users can also override it on a [per-user basis](/user/concept/#changing-the-language).

If some text strings are not translated from English, you can improve the `django.po` files of the language and [recompile them](/developer/development/#internationalization). The translation files are in the [locale](https://github.com/cloudera/hue/tree/master/desktop/core/src/desktop/locale) directories.

### Maps look and feel

Change the `leaflet_tile_layer` and `leaflet_tile_layer_attribution` properties:

```ini
[desktop]
  leaflet_tile_layer=https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}
  leaflet_tile_layer_attribution='Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
```

[Read more about it here](http://gethue.com/change-your-maps-look-and-feel/).

### Banner

Add a custom banner to the Hue web UI by setting HTML in `banner_top_html`:

```ini
[desktop]
  [[custom]]
    banner_top_html=<H4>My company's custom Hue Web UI banner</H4>
```

### Splash screen

Add a splash screen to the login page by setting HTML in `login_splash_html`:

```ini
[desktop]
  [[custom]]
    login_splash_html=WARNING: You are required to have authorization before you proceed.
```

### Custom logo

Replace the logo with your own SVG code in `logo_svg`. The SVG replaces the default logo in the top bar and on the sign-in screen. Design it to fit in a 160×40 pixel space.

```ini
[desktop]
  [[custom]]
    # e.g. <image xlink:href="/static/desktop/art/hue-logo-mini-white.png" x="0" y="0" height="40" width="160" />
    logo_svg=
```

For example, this code shows a logo made of three hearts:

```ini
[desktop]
  [[custom]]
    logo_svg='<g><path stroke="null" id="svg_1" d="m44.41215,11.43463c-4.05017,-10.71473 -17.19753,-5.90773 -18.41353,-0.5567c-1.672,-5.70253 -14.497,-9.95663 -18.411,0.5643c-4.35797,11.71793 16.891,22.23443 18.41163,23.95773c1.5181,-1.36927 22.7696,-12.43803 18.4129,-23.96533z" fill="#ffffff"/> <path stroke="null" id="svg_2" d="m98.41246,10.43463c-4.05016,-10.71473 -17.19753,-5.90773 -18.41353,-0.5567c-1.672,-5.70253 -14.497,-9.95663 -18.411,0.5643c-4.35796,11.71793 16.891,22.23443 18.41164,23.95773c1.5181,-1.36927 22.76959,-12.43803 18.41289,-23.96533z" fill="#FF5A79"/> <path stroke="null" id="svg_3" d="m154.41215,11.43463c-4.05016,-10.71473 -17.19753,-5.90773 -18.41353,-0.5567c-1.672,-5.70253 -14.497,-9.95663 -18.411,0.5643c-4.35796,11.71793 16.891,22.23443 18.41164,23.95773c1.5181,-1.36927 22.76959,-12.43803 18.41289,-23.96533z" fill="#ffffff"/> </g>'
```

[Read more about it here](http://gethue.com/hue-with-a-custom-logo/).

## Source version control

By default, Hue stores [saved documents](/user/concept/#documents) in its database. You can point Hue to a source version control system such as GitHub or Bitbucket to open and save queries.

> **Note**: This feature is experimental.

```ini
[desktop]
  [[vcs]]
    [[[git-read-only]]]
      # Base URL to the remote server
      remote_url=https://github.com/cloudera/hue/tree/master

      # Base URL to the version control API
      api_url=https://api.github.com

    [[[github]]]
      remote_url=https://github.com/cloudera/hue/tree/master
      api_url=https://api.github.com

      # Required to write back to the repository.
      # Client ID for the authorized application
      client_id=
      # Client secret for the authorized application
      client_secret=

    [[[svn]]]
      remote_url=https://github.com/cloudera/hue/tree/master
      api_url=https://api.github.com

      # Required to write back to the repository.
      client_id=
      client_secret=
```

## Slack

Currently in **beta**.

This [integration](/user/concept/#slack) helps users with their SQL queries and lets them collaborate and discuss with other users via Slack.

### Architecture

![Share to Slack Architecture](https://cdn.gethue.com/uploads/2021/04/share_to_slack_architecture.png)

One flow shares query and gist links. The bot logic runs on top of the Hue server. It listens to the events that the Slack Hue app posts to an endpoint. It processes them, for example by generating a rich preview that unfurls the links shared in Slack channels. It then sends the responses back to Slack with the Slack API.

The Smart Query Assistance block on top of the Hue server drives the other flow, SQL assistance. It is a work in progress. It is meant to answer users who ask how to find certain data tables or query them.

### Easier Slack app installation

The **Slack workspace admin** follows these steps to set up a Hue Slack app. You create the app only once. Other Hue users can then [interact](/user/concept/#slack) with the app in Slack channels.

1. Go to https://gethue.com/ and, in the last section, enter your **Hue instance hostname** (for example, `hue.gethue.com:8000`).
2. Choose the Slack workspace where you want to install the app and click **Next**.
3. Review the configuration and click **Create**.
4. Install the app in the workspace and connect it to Hue with the [last step of the manual installation](#update-your-hueini-file).

![Easier Installation GIF](https://cdn.gethue.com/uploads/2021/06/easier_installation_slack.gif)

### Manual Slack app installation

#### App manifest (YAML)

The latest manifest file is checked in [here](https://github.com/cloudera/hue/blob/master/tools/slack/manifest.yml).

#### Changes needed in the manifest

Replace the two `demo.gethue.com` values with **your Hue instance hostname**:

* Under `unfurl_domains`.
* Under `event_subscriptions`, in `request_url`: `https://<hue-instance-hostname>/desktop/slack/events/`.

#### Create your app

1. Go to https://api.slack.com/apps and click **Create New App**.
2. Choose **From an app manifest**, select the workspace where you want to install the app, and click **Next**.
3. Choose **YAML**, paste the manifest (with the changes above), and click **Next**.
4. Read the review summary. If everything is correct, click **Create**.
5. Install the app in the workspace.

#### Update your hue.ini file

1. Go to the **OAuth & Permissions** page and copy the **Bot User OAuth Token** (for example, `xoxb-xxxxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxxx`).
2. Go to the **Basic Information** page and copy the **Verification Token**.
3. Add both to the `[desktop]` section of your `hue.ini` file:

```ini
[desktop]
  [[slack]]
    is_enabled=true
    slack_verification_token=<your-slack-verification-token>
    slack_bot_user_token=<your-slack-bot-user-token>
```

Now add the Slack app to your channels and send some [query or gist links](/user/concept/#slack).
