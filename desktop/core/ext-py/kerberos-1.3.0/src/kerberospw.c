/**
 * Copyright (c) 2008 Guido Guenther <agx@sigxcpu.org>
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 **/

#include <Python.h>
#include "kerberospw.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#undef PRINTFS

extern PyObject *PwdChangeException_class;

static void set_pwchange_error(krb5_context context, krb5_error_code code)
{
    PyErr_SetObject(
        PwdChangeException_class,
        Py_BuildValue("(s:i)", krb5_get_err_text(context, code), code)
    );
}

/* Inspired by krb5_verify_user from Heimdal */
static krb5_error_code verify_krb5_user(
    krb5_context context,
    krb5_principal principal,
    const char *password,
    const char *service,
    krb5_creds* creds
) {
    krb5_get_init_creds_opt gic_options;
    krb5_error_code code;
    int ret = 0;
    
#ifdef PRINTFS
    {
        char *name = NULL;
        code = krb5_unparse_name(context, principal, &name);
        if (!code) {
            printf("Trying to get TGT for user %s\n", name);
        }
        free(name);
    }
#endif

    krb5_get_init_creds_opt_init(&gic_options);
    krb5_get_init_creds_opt_set_forwardable(&gic_options, 0);
    krb5_get_init_creds_opt_set_proxiable(&gic_options, 0);
    krb5_get_init_creds_opt_set_renew_life(&gic_options, 0);

    memset(creds, 0, sizeof(krb5_creds));
    
    code = krb5_get_init_creds_password(
        context, creds, principal,
        (char *)password, NULL, NULL, 0,
        (char *)service, &gic_options
    );
    if (code) {
        set_pwchange_error(context, code);
        goto end;
    }
    ret = 1; /* success */

end:
    return ret;
}

int change_user_krb5pwd(
    const char *user, const char* oldpswd, const char *newpswd
) {
    krb5_context    kcontext = NULL;
    krb5_error_code code;
    krb5_principal  client = NULL;
    krb5_creds      creds;
    int             ret = 0;
    int             bytes = 0;
    char            *name = NULL;

    const char* service = "kadmin/changepw";
    int result_code;
    krb5_data result_code_string, result_string;

    code = krb5_init_context(&kcontext);
    if (code) {
        PyErr_SetObject(
            PwdChangeException_class,
            Py_BuildValue(
                "((s:i))", "Cannot initialize Kerberos5 context", code
            )
        );
        return 0;
    }

    name = (char *)malloc(256);
    if (name == NULL)
    {
        PyErr_NoMemory();
        goto end;
    }
    snprintf(name, 256, "%s", user);
        
    code = krb5_parse_name(kcontext, name, &client);
    if (code) {
        set_pwchange_error(kcontext, code);
        goto end;
    }

    code = verify_krb5_user(kcontext, client, oldpswd, service, &creds);
    if (! code) {  /* exception set by verify_krb5_user */
        goto end;
    }

    code = krb5_change_password(kcontext, &creds, (char*)newpswd,
                                &result_code, &result_code_string, &result_string);
    if (code) {
        set_pwchange_error(kcontext, code);
        goto end;
    }
    if (result_code) {
        char *message = NULL;
        bytes = asprintf(
            &message, "%.*s: %.*s",
            (int) result_code_string.length,
            (char *) result_code_string.data,
            (int) result_string.length,
            (char *) result_string.data
        );
        if (bytes == -1)
        {
            PyErr_NoMemory();
        }
        else
        {
            PyErr_SetObject(
                PwdChangeException_class,
                Py_BuildValue("((s:i))", message, result_code)
            );
            free(message);
        }
        goto end;
    }

    ret = 1; /* success */

end:
#ifdef PRINTFS
    printf("%s: ret=%d user=%s\n", __FUNCTION__, ret, name);
#endif

    if (name) {
        free(name);
    }
    if (client) {
        krb5_free_principal(kcontext, client);
    }
    krb5_free_context(kcontext);

    return ret;
}
