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

import huePubSub from './huePubSub';

describe('huePubSub', () => {
  beforeEach(() => {
    const topics = huePubSub.getTopics();
    Object.keys(topics).forEach(key => {
      huePubSub.removeAll(key);
    });
  });

  describe('subscribe and publish', () => {
    it('should call listener when topic is published', () => {
      const listener = jest.fn();
      huePubSub.subscribe('test-topic', listener);
      huePubSub.publish('test-topic', { data: 'test' });
      expect(listener).toHaveBeenCalledWith({ data: 'test' });
    });

    it('should call multiple listeners for the same topic', () => {
      const listener1 = jest.fn();
      const listener2 = jest.fn();
      huePubSub.subscribe('test-topic', listener1);
      huePubSub.subscribe('test-topic', listener2);
      huePubSub.publish('test-topic', 'test data');
      expect(listener1).toHaveBeenCalledWith('test data');
      expect(listener2).toHaveBeenCalledWith('test data');
    });

    it('should not call listener if topic does not exist', () => {
      const listener = jest.fn();
      huePubSub.subscribe('test-topic', listener);
      huePubSub.publish('other-topic', 'test');
      expect(listener).not.toHaveBeenCalled();
    });
  });

  describe('remove subscription', () => {
    it('should not call listener after subscription is removed', () => {
      const listener = jest.fn();
      const subscription = huePubSub.subscribe('test-topic', listener);
      subscription.remove();
      huePubSub.publish('test-topic', 'test');
      expect(listener).not.toHaveBeenCalled();
    });

    it('should handle multiple subscriptions removal correctly (bug fix test)', () => {
      const listener1 = jest.fn();
      const listener2 = jest.fn();
      const listener3 = jest.fn();

      huePubSub.subscribe('test-topic', listener1);
      const sub2 = huePubSub.subscribe('test-topic', listener2);
      huePubSub.subscribe('test-topic', listener3);

      // Remove the middle subscription
      sub2.remove();

      // Publish and verify only listener1 and listener3 are called
      huePubSub.publish('test-topic', 'test');
      expect(listener1).toHaveBeenCalledWith('test');
      expect(listener2).not.toHaveBeenCalled();
      expect(listener3).toHaveBeenCalledWith('test');
    });

    it('should handle removal of first subscription correctly', () => {
      const listener1 = jest.fn();
      const listener2 = jest.fn();
      const listener3 = jest.fn();

      const sub1 = huePubSub.subscribe('test-topic', listener1);
      huePubSub.subscribe('test-topic', listener2);
      huePubSub.subscribe('test-topic', listener3);

      sub1.remove();

      huePubSub.publish('test-topic', 'test');
      expect(listener1).not.toHaveBeenCalled();
      expect(listener2).toHaveBeenCalledWith('test');
      expect(listener3).toHaveBeenCalledWith('test');
    });

    it('should handle removing same subscription multiple times', () => {
      const listener = jest.fn();
      const subscription = huePubSub.subscribe('test-topic', listener);
      subscription.remove();
      subscription.remove(); // Should not throw error
      huePubSub.publish('test-topic', 'test');
      expect(listener).not.toHaveBeenCalled();
    });
  });

  describe('subscribeOnce', () => {
    it('should call listener only once', () => {
      const listener = jest.fn();
      huePubSub.subscribeOnce('test-topic', listener, 'test-app');
      huePubSub.publish('test-topic', 'first');
      huePubSub.publish('test-topic', 'second');
      expect(listener).toHaveBeenCalledTimes(1);
      expect(listener).toHaveBeenCalledWith('first');
    });

    it('should auto-remove subscription after first call', () => {
      const listener = jest.fn();
      huePubSub.subscribeOnce('test-topic', listener, 'test-app');
      huePubSub.publish('test-topic', 'test');
      const topics = huePubSub.getTopics();
      expect(topics['test-topic'].length).toBe(0);
    });
  });

  describe('removeAll', () => {
    it('should remove all subscriptions for a topic', () => {
      const listener1 = jest.fn();
      const listener2 = jest.fn();
      huePubSub.subscribe('test-topic', listener1);
      huePubSub.subscribe('test-topic', listener2);
      huePubSub.removeAll('test-topic');
      huePubSub.publish('test-topic', 'test');
      expect(listener1).not.toHaveBeenCalled();
      expect(listener2).not.toHaveBeenCalled();
    });
  });

  describe('pauseAppSubscribers and resumeAppSubscribers', () => {
    it('should pause app subscribers', () => {
      const listener = jest.fn();
      huePubSub.subscribe('test-topic', listener, 'test-app');
      huePubSub.pauseAppSubscribers('test-app');
      huePubSub.publish('test-topic', 'test');
      expect(listener).not.toHaveBeenCalled();
    });

    it('should resume app subscribers', () => {
      const listener = jest.fn();
      huePubSub.subscribe('test-topic', listener, 'test-app');
      huePubSub.pauseAppSubscribers('test-app');
      huePubSub.resumeAppSubscribers('test-app');
      huePubSub.publish('test-topic', 'test');
      expect(listener).toHaveBeenCalledWith('test');
    });

    it('should only affect specific app subscribers', () => {
      const listener1 = jest.fn();
      const listener2 = jest.fn();
      huePubSub.subscribe('test-topic', listener1, 'app1');
      huePubSub.subscribe('test-topic', listener2, 'app2');
      huePubSub.pauseAppSubscribers('app1');
      huePubSub.publish('test-topic', 'test');
      expect(listener1).not.toHaveBeenCalled();
      expect(listener2).toHaveBeenCalledWith('test');
    });
  });

  describe('clearAppSubscribers', () => {
    it('should clear all subscribers for an app', () => {
      const listener1 = jest.fn();
      const listener2 = jest.fn();
      huePubSub.subscribe('test-topic', listener1, 'test-app');
      huePubSub.subscribe('test-topic', listener2, 'other-app');
      huePubSub.clearAppSubscribers('test-app');
      huePubSub.publish('test-topic', 'test');
      expect(listener1).not.toHaveBeenCalled();
      expect(listener2).toHaveBeenCalledWith('test');
    });

    it('should work correctly with remove() after clearAppSubscribers', () => {
      const listener1 = jest.fn();
      const listener2 = jest.fn();
      const sub1 = huePubSub.subscribe('test-topic', listener1, 'test-app');
      huePubSub.subscribe('test-topic', listener2, 'other-app');
      huePubSub.clearAppSubscribers('test-app');
      sub1.remove(); // Should not throw error
      huePubSub.publish('test-topic', 'test');
      expect(listener2).toHaveBeenCalledWith('test');
    });
  });
});
