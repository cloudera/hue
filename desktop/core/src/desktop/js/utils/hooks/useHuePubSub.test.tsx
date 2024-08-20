import { renderHook, act } from '@testing-library/react';
import { useHuePubSub } from './useHuePubSub';
import huePubSub from '../huePubSub';
import noop from '../timing/noop';

describe('useHuePubSub', () => {
  const originalSubscribe = huePubSub.subscribe;
  let publishCallback: (a: string) => void;
  const remove = jest.fn();

  const subscribeMock = jest.fn().mockImplementation((topic, callback) => {
    publishCallback = callback;
    return { remove };
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

  test('only subscribes once per hook lifecycle', () => {
    expect(huePubSub.subscribe).toBeCalledTimes(0);

    const { rerender } = renderHook(() => useHuePubSub({ topic: 'my.test.topic' }));
    expect(huePubSub.subscribe).toHaveBeenCalledWith('my.test.topic', expect.anything(), undefined);
    expect(huePubSub.subscribe).toHaveBeenCalledTimes(1);
    expect(remove).not.toHaveBeenCalled();

    rerender();
    expect(remove).toHaveBeenCalled();
    expect(huePubSub.subscribe).toHaveBeenCalledTimes(2);
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

  test('triggers a callback with the info when a message is published', () => {
    let callbackCalled = false;
    renderHook(() =>
      useHuePubSub<string>({
        topic: 'my.test.topic',
        callback: a => {
          expect(a).toEqual('some info');
          callbackCalled = true;
        }
      })
    );

    act(() => {
      publishCallback('some info');
    });

    expect(callbackCalled).toBeTruthy();
  });

  test("when callback is provided there won't be a state update", () => {
    const { result } = renderHook(() =>
      useHuePubSub<string>({
        topic: 'my.test.topic',
        callback: noop
      })
    );

    act(() => {
      publishCallback('some info');
    });

    expect(result.current).not.toEqual('some info');
  });
});
