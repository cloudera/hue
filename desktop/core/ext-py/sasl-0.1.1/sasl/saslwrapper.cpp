/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
*/

#include "saslwrapper.h"
#include <sasl/sasl.h>
#include <sstream>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <iostream>

using namespace std;
using namespace saslwrapper;

namespace saslwrapper {

    class ClientImpl {
        friend class Client;
        ClientImpl() : conn(0), cbIndex(0), maxBufSize(65535), minSsf(0), maxSsf(65535), externalSsf(0), secret(0) {}
        ~ClientImpl() { if (conn) sasl_dispose(&conn); conn = 0; }
        bool setAttr(const string& key, const string& value);
        bool setAttr(const string& key, uint32_t value);
        bool init();
        bool start(const string& mechList, output_string& chosen, output_string& initialResponse);
        bool step(const string& challenge, output_string& response);
        bool encode(const string& clearText, output_string& cipherText);
        bool decode(const string& cipherText, output_string& clearText);
        bool getUserId(output_string& userId);
        void getError(output_string& error);

        void addCallback(unsigned long id, void* proc);
        void lastCallback() { addCallback(SASL_CB_LIST_END, 0); }
        void setError(const string& context, int code, const string& text = "", const string& text2 = "");
        void interact(sasl_interact_t* prompt);

        static int cbName(void *context, int id, const char **result, unsigned *len);
        static int cbPassword(sasl_conn_t *conn, void *context, int id, sasl_secret_t **psecret);

        static bool initialized;
        sasl_conn_t* conn;
        sasl_callback_t callbacks[8];
        int cbIndex;
        string error;
        string serviceName;
        string userName;
        string authName;
        string password;
        string hostName;
        string externalUserName;
        uint32_t maxBufSize;
        uint32_t minSsf;
        uint32_t maxSsf;
        uint32_t externalSsf;
        sasl_secret_t* secret;
    };
}

bool ClientImpl::initialized = false;

bool ClientImpl::init()
{
    int result;

    if (!initialized) {
        initialized = true;
        result = sasl_client_init(0);
        if (result != SASL_OK) {
            setError("sasl_client_init", result, sasl_errstring(result, 0, 0));
            return false;
        }
    }

    int cbIndex = 0;

    addCallback(SASL_CB_GETREALM, 0);
    if (!userName.empty()) {
        addCallback(SASL_CB_USER, (void*) cbName);
        addCallback(SASL_CB_AUTHNAME, (void*) cbName);

        if (!password.empty())
            addCallback(SASL_CB_PASS, (void*) cbPassword);
        else
            addCallback(SASL_CB_PASS, 0);
    }
    lastCallback();

    unsigned flags;

    flags = 0;
    if (!authName.empty() && authName != userName)
        flags |= SASL_NEED_PROXY;

    result = sasl_client_new(serviceName.c_str(), hostName.c_str(), 0, 0, callbacks, flags, &conn);
    if (result != SASL_OK) {
        setError("sasl_client_new", result, sasl_errstring(result, 0, 0));
        return false;
    }

    sasl_security_properties_t secprops;

    secprops.min_ssf = minSsf;
    secprops.max_ssf = maxSsf;
    secprops.maxbufsize = maxBufSize;
    secprops.property_names = 0;
    secprops.property_values = 0;
    secprops.security_flags = 0;

    result = sasl_setprop(conn, SASL_SEC_PROPS, &secprops);
    if (result != SASL_OK) {
        setError("sasl_setprop(SASL_SEC_PROPS)", result);
        sasl_dispose(&conn);
        conn = 0;
        return false;
    }

    if (!externalUserName.empty()) {
        result = sasl_setprop(conn, SASL_AUTH_EXTERNAL, externalUserName.c_str());
        if (result != SASL_OK) {
            setError("sasl_setprop(SASL_AUTH_EXTERNAL)", result);
            sasl_dispose(&conn);
            conn = 0;
            return false;
        }

        result = sasl_setprop(conn, SASL_SSF_EXTERNAL, &externalSsf);
        if (result != SASL_OK) {
            setError("sasl_setprop(SASL_SSF_EXTERNAL)", result);
            sasl_dispose(&conn);
            conn = 0;
            return false;
        }
    }

    return true;
}

bool ClientImpl::setAttr(const string& key, const string& value)
{
    if (key == "service")
        serviceName = value;
    else if (key == "username")
        userName = value;
    else if (key == "authname")
        authName = value;
    else if (key == "password") {
        password = value;
        free(secret);
        secret = (sasl_secret_t*) malloc(sizeof(sasl_secret_t) + password.length());
    }
    else if (key == "host")
        hostName = value;
    else if (key == "externaluser")
        externalUserName = value;
    else {
        setError("setAttr", -1, "Unknown string attribute name", key);
        return false;
    }

    return true;
}

bool ClientImpl::setAttr(const string& key, uint32_t value)
{
    if (key == "minssf")
        minSsf = value;
    else if (key == "maxssf")
        maxSsf = value;
    else if (key == "externalssf")
        externalSsf = value;
    else if (key == "maxbufsize")
        maxBufSize = value;
    else {
        setError("setAttr", -1, "Unknown integer attribute name", key);
        return false;
    }

    return true;
}

bool ClientImpl::start(const string& mechList, output_string& chosen, output_string& initialResponse)
{
    int result;
    sasl_interact_t* prompt = 0;
    const char* resp;
    const char* mech;
    unsigned int len;

    do {
        result = sasl_client_start(conn, mechList.c_str(), &prompt, &resp, &len, &mech);
        if (result == SASL_INTERACT)
            interact(prompt);
    } while (result == SASL_INTERACT);
    if (result != SASL_OK && result != SASL_CONTINUE) {
        setError("sasl_client_start", result);
        return false;
    }

    chosen = string(mech);
    initialResponse = string(resp, len);
    return true;
}

bool ClientImpl::step(const string& challenge, output_string& response)
{
    int result;
    sasl_interact_t* prompt = 0;
    const char* resp;
    unsigned int len;

    do {
        result = sasl_client_step(conn, challenge.c_str(), challenge.size(), &prompt, &resp, &len);
        if (result == SASL_INTERACT)
            interact(prompt);
    } while (result == SASL_INTERACT);
    if (result != SASL_OK && result != SASL_CONTINUE) {
        setError("sasl_client_step", result);
        return false;
    }

    response = string(resp, len);
    return true;
}

bool ClientImpl::encode(const string& clearText, output_string& cipherText)
{
    const char* output;
    unsigned int outlen;
    int result = sasl_encode(conn, clearText.c_str(), clearText.size(), &output, &outlen);
    if (result != SASL_OK) {
        setError("sasl_encode", result);
        return false;
    }
    cipherText = string(output, outlen);
    return true;
}

bool ClientImpl::decode(const string& cipherText, output_string& clearText)
{
    const char* input = cipherText.c_str();
    unsigned int inLen = cipherText.size();
    unsigned int remaining = inLen;
    const char* cursor = input;
    const char* output;
    unsigned int outlen;

    clearText = string();
    while (remaining > 0) {
        unsigned int segmentLen = (remaining < maxBufSize) ? remaining : maxBufSize;
        int result = sasl_decode(conn, cursor, segmentLen, &output, &outlen);
        if (result != SASL_OK) {
            setError("sasl_decode", result);
            return false;
        }
        clearText = clearText + string(output, outlen);
        cursor += segmentLen;
        remaining -= segmentLen;
    }
    return true;
}

bool ClientImpl::getUserId(output_string& userId)
{
    int result;
    const char* operName;

    result = sasl_getprop(conn, SASL_USERNAME, (const void**) &operName);
    if (result != SASL_OK) {
        setError("sasl_getprop(SASL_USERNAME)", result);
        return false;
    }

    userId = string(operName);
    return true;
}

void ClientImpl::getError(output_string& _error)
{
    _error = error;
    error.clear();
}

void ClientImpl::addCallback(unsigned long id, void* proc)
{
    callbacks[cbIndex].id = id;
    callbacks[cbIndex].proc = (int (*)()) proc;
    callbacks[cbIndex].context = this;
    cbIndex++;
}

void ClientImpl::setError(const string& context, int code, const string& text, const string& text2)
{
    stringstream err;
    string etext(text.empty() ? sasl_errdetail(conn) : text);
    err << "Error in " << context << " (" << code << ") " << etext;
    if (!text2.empty())
        err << " - " << text2;
    error = err.str();
}

void ClientImpl::interact(sasl_interact_t* prompt)
{
    string output;
    char* input;

    if (prompt->id == SASL_CB_PASS) {
        string ppt(prompt->prompt);
        ppt += ": ";
        char* pass = getpass(ppt.c_str());
        output = string(pass);
    } else {
        cout << prompt->prompt;
        if (prompt->defresult)
            cout << " [" << prompt->defresult << "]";
        cout << ": ";
        cin >> output;
    }
    prompt->result = output.c_str();
    prompt->len = output.length();
}

int ClientImpl::cbName(void *context, int id, const char **result, unsigned *len)
{
    ClientImpl* impl = (ClientImpl*) context;

    if (id == SASL_CB_USER || (id == SASL_CB_AUTHNAME && impl->authName.empty())) {
        *result = impl->userName.c_str();
        //*len    = impl->userName.length();
    } else if (id == SASL_CB_AUTHNAME) {
        *result = impl->authName.c_str();
        //*len    = impl->authName.length();
    }

    return SASL_OK;
}

int ClientImpl::cbPassword(sasl_conn_t *conn, void *context, int id, sasl_secret_t **psecret)
{
    ClientImpl* impl = (ClientImpl*) context;
    size_t length = impl->password.length();

    if (id == SASL_CB_PASS) {
        impl->secret->len = length;
        ::memcpy(impl->secret->data, impl->password.c_str(), length);
    } else
        impl->secret->len = 0;

    *psecret = impl->secret;
    return SASL_OK;
}


//==========================================================
// WRAPPERS
//==========================================================

Client::Client() : impl(new ClientImpl()) {}
Client::~Client() { delete impl; }
bool Client::setAttr(const string& key, const string& value) { return impl->setAttr(key, value); }
bool Client::setAttr(const string& key, uint32_t value) { return impl->setAttr(key, value); }
bool Client::init() { return impl->init(); }
bool Client::start(const string& mechList, output_string& chosen, output_string& initialResponse) { return impl->start(mechList, chosen, initialResponse); }
bool Client::step(const string& challenge, output_string& response) { return impl->step(challenge, response); }
bool Client::encode(const string& clearText, output_string& cipherText) { return impl->encode(clearText, cipherText); }
bool Client::decode(const string& cipherText, output_string& clearText) { return impl->decode(cipherText, clearText); }
bool Client::getUserId(output_string& userId) { return impl->getUserId(userId); }
void Client::getError(output_string& error) { impl->getError(error); }

