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

#include <stdint.h>
#include <string>

namespace saslwrapper {

    /**
     * The following type is used for output arguments (that are strings).  The fact that it has
     * a unique name is used in a SWIG typemap to indicate output arguments.  For scripting languages
     * such as Python and Ruby (which do not support output arguments), the outputs are placed in and
     * array that is returned by the function.  For example, a function that looks like:
     *
     *      bool function(const string& input, output_string& out1, output_string& out2);
     *
     * would be called (in Python) like this:
     *
     *      boolResult, out1, out2 = function(input)
     */
    typedef std::string output_string;
    class ClientImpl;

    class Client {
    public:

        Client();
        ~Client();

        /**
         * Set attributes to be used in authenticating the session.  All attributes should be set
         * before init() is called.
         *
         * @param key Name of attribute being set
         * @param value Value of attribute being set
         * @return true iff success.  If false is returned, call getError() for error details.
         *
         * Available attribute keys:
         *
         *    service      - Name of the service being accessed
         *    username     - User identity for authentication
         *    authname     - User identity for authorization (if different from username)
         *    password     - Password associated with username
         *    host         - Fully qualified domain name of the server host
         *    maxbufsize   - Maximum receive buffer size for the security layer
         *    minssf       - Minimum acceptable security strength factor (integer)
         *    maxssf       - Maximum acceptable security strength factor (integer)
         *    externalssf  - Security strength factor supplied by external mechanism (i.e. SSL/TLS)
         *    externaluser - Authentication ID (of client) as established by external mechanism
         */
        bool setAttr(const std::string& key, const std::string& value);
        bool setAttr(const std::string& key, uint32_t value);

        /**
         * Initialize the client object.  This should be called after all of the properties have been set.
         *
         * @return true iff success.  If false is returned, call getError() for error details.
         */
        bool init();

        /**
         * Start the SASL exchange with the server.
         *
         * @param mechList List of mechanisms provided by the server
         * @param chosen The mechanism chosen by the client
         * @param initialResponse Initial block of data to send to the server
         *
         * @return true iff success.  If false is returned, call getError() for error details.
         */
        bool start(const std::string& mechList, output_string& chosen, output_string& initialResponse);

        /**
         * Step the SASL handshake.
         *
         * @param challenge The challenge supplied by the server
         * @param response (output) The response to be sent back to the server
         *
         * @return true iff success.  If false is returned, call getError() for error details.
         */
        bool step(const std::string& challenge, output_string& response);

        /**
         * Encode data for secure transmission to the server.
         *
         * @param clearText Clear text data to be encrypted
         * @param cipherText (output) Encrypted data to be transmitted
         *
         * @return true iff success.  If false is returned, call getError() for error details.
         */
        bool encode(const std::string& clearText, output_string& cipherText);

        /**
         * Decode data received from the server.
         *
         * @param cipherText Encrypted data received from the server
         * @param clearText (output) Decrypted clear text data 
         *
         * @return true iff success.  If false is returned, call getError() for error details.
         */
        bool decode(const std::string& cipherText, output_string& clearText);

        /**
         * Get the user identity (used for authentication) associated with this session.
         * Note that this is particularly useful for single-sign-on mechanisms in which the 
         * username is not supplied by the application.
         *
         * @param userId (output) Authenticated user ID for this session.
         */
        bool getUserId(output_string& userId);

        /**
         * Get error message for last error.
         * This function will return the last error message then clear the error state.
         * If there was no error or the error state has been cleared, this function will output
         * an empty string.
         *
         * @param error Error message string
         */
        void getError(output_string& error);

    private:
        ClientImpl* impl;

        // Declare private copy constructor and assignment operator.  Ensure that this
        // class is non-copyable.
        Client(const Client&);
        const Client& operator=(const Client&);
    };

}
