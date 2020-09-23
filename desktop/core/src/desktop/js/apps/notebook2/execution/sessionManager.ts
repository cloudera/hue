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

import {
  AuthRequest,
  closeSession,
  createSession,
  Session,
  SessionProperty
} from 'apps/notebook2/execution/apiUtils';
import huePubSub from 'utils/huePubSub';

class SessionManager {
  knownSessionPromises: { [key: string]: Promise<Session> } = {};

  /**
   * Gets an existing session or creates a new one if there is no session.
   */
  async getSession(options: { type: string; properties?: SessionProperty[] }): Promise<Session> {
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
  async createDetachedSession(options: {
    type: string;
    properties?: SessionProperty[];
    preventAuthModal?: boolean;
  }): Promise<Session> {
    return new Promise(async (resolve, reject) => {
      const sessionToCreate = {
        type: options.type,
        properties: options.properties || []
      };

      const sessionOrAuth = await createSession(sessionToCreate);
      if ('auth' in sessionOrAuth && sessionOrAuth.auth) {
        const auth = sessionOrAuth as AuthRequest;
        if (!options.preventAuthModal) {
          huePubSub.publish('show.session.auth.modal', {
            message: auth.message,
            session: sessionToCreate,
            resolve: resolve,
            reject: reject
          });
        } else {
          reject(auth);
        }
      } else {
        resolve(sessionOrAuth as Session);
      }
    });
  }

  updateSession(session: Session) {
    this.knownSessionPromises[session.type] = Promise.resolve(session);
  }

  async getAllSessions(): Promise<Session[]> {
    const promises = Object.keys(this.knownSessionPromises).map(
      key => this.knownSessionPromises[key]
    );
    return Promise.all(promises);
  }

  async restartSession(session: Session): Promise<Session> {
    await this.closeSession(session);
    return this.getSession(session);
  }

  hasSession(type: string): boolean {
    return !!this.knownSessionPromises[type];
  }

  async closeSession(session: Session): Promise<void> {
    if (this.hasSession(session.type)) {
      delete this.knownSessionPromises[session.type];
    }
    await closeSession({ session: session, silenceErrors: true });
  }
}

const instance = new SessionManager();

export default instance;
