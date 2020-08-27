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

import { CancellablePromise } from 'api/cancellablePromise';
import { CLOSE_SESSION_API } from 'api/urls';
import { AuthRequest, Session, SessionProperty } from './apiUtils';

import * as ApiUtils from './apiUtils';
import * as ApiUtilsV2 from 'api/apiUtilsV2';
import sessionManager from './sessionManager';

describe('sessionManager.ts', () => {
  let spy: jest.SpyInstance<
    Promise<AuthRequest | Session>,
    [
      {
        type: string;
        properties?: SessionProperty[] | undefined;
        silenceErrors?: boolean | undefined;
      }
    ]
  >;

  beforeEach(() => {
    // sessionManager is a singleton so we need to clear out sessions between tests
    sessionManager.knownSessionPromises = {};
    const sessionCount: { [key: string]: number } = {};
    const getSessionCount = (type: string) => {
      if (!sessionCount[type]) {
        sessionCount[type] = 0;
      }
      return sessionCount[type]++;
    };
    spy = jest.spyOn(ApiUtils, 'createSession').mockImplementation(
      async (options: {
        type: string;
        properties?: SessionProperty[];
        silenceErrors?: boolean;
      }): Promise<Session | AuthRequest> =>
        Promise.resolve({
          session_id: options.type + '_' + getSessionCount(options.type),
          type: options.type,
          properties: options.properties || [],
          reuse_session: true,
          id: 0
        })
    );
  });

  afterEach(() => {
    sessionManager.knownSessionPromises = {};
    spy.mockClear();
  });

  it('should create detached sessions', async () => {
    const mockProperties: unknown[] = [{ key: 'someKey', value: ['someValue'] }];
    const sessionDetails = {
      type: 'impala',
      properties: mockProperties as SessionProperty[]
    };

    expect((await sessionManager.getAllSessions()).length).toEqual(0);

    const session = await sessionManager.createDetachedSession(sessionDetails);
    expect(session.session_id).toEqual('impala_0');
    expect(session.properties.length).toEqual(1);
    expect(session.properties[0].key).toEqual((mockProperties[0] as SessionProperty).key);
    expect(session.properties[0].value).toEqual((mockProperties[0] as SessionProperty).value);

    expect((await sessionManager.getAllSessions()).length).toEqual(0);
    expect(sessionManager.hasSession('impala')).toBeFalsy();
    expect(ApiUtils.createSession).toHaveBeenCalledWith(sessionDetails);
  });

  it('should keep one sessions instance per type', async () => {
    expect((await sessionManager.getAllSessions()).length).toEqual(0);

    let session = await sessionManager.getSession({ type: 'impala' });

    expect(session.session_id).toEqual('impala_0');

    session = await sessionManager.getSession({ type: 'impala' });

    expect(session.session_id).toEqual('impala_0');

    expect((await sessionManager.getAllSessions()).length).toEqual(1);
    expect(sessionManager.hasSession('impala')).toBeTruthy();
    expect(ApiUtils.createSession).toHaveBeenCalledTimes(1);
  });

  it('should keep track of multiple instance per type', async () => {
    expect((await sessionManager.getAllSessions()).length).toEqual(0);

    let session = await sessionManager.getSession({ type: 'impala' });

    expect(session.session_id).toEqual('impala_0');

    session = await sessionManager.getSession({ type: 'hive' });

    expect(session.session_id).toEqual('hive_0');

    expect((await sessionManager.getAllSessions()).length).toEqual(2);
    expect(sessionManager.hasSession('impala')).toBeTruthy();
    expect(sessionManager.hasSession('hive')).toBeTruthy();
    expect(ApiUtils.createSession).toHaveBeenCalledTimes(2);
  });

  it('should stop tracking sessions when closed', async () => {
    expect((await sessionManager.getAllSessions()).length).toEqual(0);

    // Create a session
    const session = await sessionManager.getSession({ type: 'impala' });

    expect(session.session_id).toEqual('impala_0');
    expect(sessionManager.hasSession('impala')).toBeTruthy();

    //(url, data, options) => {
    //       expect(JSON.parse(data.session).session_id).toEqual(session.session_id);
    //       expect(options.silenceErrors).toBeTruthy();
    //       expect(url).toEqual(CLOSE_SESSION_API);
    //       return new $.Deferred().resolve().promise();
    //     }
    // Close the session

    const postSpy = jest.spyOn(ApiUtilsV2, 'simplePost').mockImplementation(
      (
        url: string,
        data: unknown,
        options?: { dataType?: string; silenceErrors?: boolean; ignoreSuccessErrors?: boolean }
      ): CancellablePromise<unknown> => {
        expect(JSON.parse((data as { session: string }).session).session_id).toEqual(
          session.session_id
        );
        expect(options && options.silenceErrors).toBeTruthy();
        expect(url).toEqual(CLOSE_SESSION_API);
        return new CancellablePromise(resolve => {
          resolve();
        });
      }
    );
    await sessionManager.closeSession(session);

    expect(sessionManager.hasSession('impala')).toBeFalsy();
    expect(ApiUtils.createSession).toHaveBeenCalledTimes(1);
    expect(ApiUtilsV2.simplePost).toHaveBeenCalledTimes(1);
    postSpy.mockClear();
  });

  it('should be able to restart sessions', async () => {
    expect((await sessionManager.getAllSessions()).length).toEqual(0);

    // Create a session
    let session = await sessionManager.getSession({ type: 'impala' });

    expect(session.session_id).toEqual('impala_0');
    expect(sessionManager.hasSession('impala')).toBeTruthy();

    // Restart the session
    const postSpy = jest.spyOn(ApiUtilsV2, 'simplePost').mockImplementation(
      (): CancellablePromise<unknown> =>
        new CancellablePromise(resolve => {
          resolve();
        })
    );
    session = await sessionManager.restartSession(session);

    expect(session.session_id).toEqual('impala_1');
    expect(sessionManager.hasSession('impala')).toBeTruthy();

    expect(ApiUtils.createSession).toHaveBeenCalledTimes(2);
    expect(ApiUtilsV2.simplePost).toHaveBeenCalledTimes(1);
    postSpy.mockClear();
  });
});
