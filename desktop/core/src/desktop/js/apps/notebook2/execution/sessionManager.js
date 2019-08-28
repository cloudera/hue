// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import apiHelper from 'api/apiHelper';
import huePubSub from 'utils/huePubSub';

class SessionManager {
  constructor() {
    this.knownSessionPromises = {};
  }
  /**
   * @typedef SessionProperty
   * @property {Array<*>} [defaultValue]
   * @property {String} [help_text]
   * @property {String} key
   * @property {Boolean} [multiple]
   * @property {String} [nice_name]
   * @property {Array<*>} [options]
   * @property {String} [type]
   * @property {Array<*>} value
   */

  /**
   * @typedef Session
   * @property {Object.<string, string>} configuration
   * @property {string} http_addr
   * @property {number} id
   * @property {Array<SessionProperty>} properties
   * @property {boolean} reuse_session
   * @property {string} session_id
   * @property {string} type
   */

  /**
   * Gets an existing session or creates a new one if there is no session.
   *
   * @param {Object} options
   * @param {String} options.type
   * @param {Array<SessionProperty>} [options.properties] - Default []
   *
   * @return {Promise<Session>}
   */
  async getSession(options) {
    if (!this.knownSessionPromises[options.type]) {
      this.knownSessionPromises[options.type] = this.createDetachedSession(options);
      // Sessions that fail
      this.knownSessionPromises[options.type].catch(() => {
        delete this.knownSessionPromises[options.type];
      });
    }
    return this.knownSessionPromises[options.type];
  }

  /**
   * Creates a new detached session
   *
   * @param {Object} options
   * @param {String} options.type
   * @param {boolean} [options.preventAuthModal] - Default false
   * @param {Array<SessionProperty>} [options.properties] - Default []
   *
   * @return {Promise<Session>}
   */
  async createDetachedSession(options) {
    return new Promise((resolve, reject) => {
      const sessionToCreate = {
        type: options.type,
        properties: options.properties || []
      };
      apiHelper
        .createSession(sessionToCreate)
        .then(resolve)
        .catch(reason => {
          if (reason && reason.auth) {
            // The auth modal will resolve or reject
            if (!options.preventAuthModal) {
              huePubSub.publish('show.session.auth.modal', {
                message: reason.message,
                session: sessionToCreate,
                resolve: resolve,
                reject: reject
              });
            }
          } else {
            reject(reason);
          }
        });
    });
  }

  async getAllSessions() {
    const promises = Object.keys(this.knownSessionPromises).map(
      key => this.knownSessionPromises[key]
    );
    return Promise.all(promises);
  }

  async restartSession(session) {
    await this.closeSession(session);
    return this.getSession({ type: session.type, properties: session.properties });
  }

  hasSession(type) {
    return !!this.knownSessionPromises[type];
  }

  async closeSession(session) {
    if (this.hasSession(session.type)) {
      delete this.knownSessionPromises[session.type];
    }
    await apiHelper.closeSession({ session: session, silenceErrors: true });
  }
}

const instance = new SessionManager();

export default instance;
