import { renderHook, act } from '@testing-library/react';
import { useHuePubSub } from './useHuePubSub';
import huePubSub from '../utils/huePubSub';

describe('useHuePubSub', () => {
  const originalSubscribe = huePubSub.subscribe;
  let publishCallback;

  const subscribeMock = jest.fn().mockImplementation((topic, callback) => {
    publishCallback = callback;
  });

  beforeAll(() => {
    huePubSub.subscribe = subscribeMock;
  });

  afterEach(() => {
    subscribeMock.mockClear();
  });

  afterAll(() => {
    huePubSub.subscribe = originalSubscribe;
  });

  test('only subscribes once', () => {
    expect(huePubSub.subscribe).toBeCalledTimes(0);

    const { result, rerender } = renderHook(() => useHuePubSub({ topic: 'my.test.topic' }));
    expect(huePubSub.subscribe).toHaveBeenCalledWith('my.test.topic', expect.anything());
    expect(huePubSub.subscribe).toHaveBeenCalledTimes(1);

    rerender();
    expect(huePubSub.subscribe).toHaveBeenCalledTimes(1);
  });

  test('initial state is undefined', () => {
    const { result } = renderHook(() => useHuePubSub({ topic: 'my.test.topic' }));
    expect(result.current).toBeUndefined();
  });

  test('triggers a state update with the info when a message is published', () => {
    const { result } = renderHook(() => useHuePubSub({ topic: 'my.test.topic' }));

    act(() => {
      publishCallback('some info');
    });

    expect(result.current).toEqual('some info');
  });
});
