import * as ApiUtils from '../api/utils';

import * as HueConfig from '../config/hueConfig';

// Since the our hueAnalytics is globally mocked in jest.init.js
// we need to use requireActual when testing the actual hueAnalytics module
const hueAnalyticsModule = jest.requireActual('./hueAnalytics');
const { hueAnalytics, setupGlobalListenersForAnalytics } = hueAnalyticsModule;

describe('hueAnalytics', () => {
  let windowSpy;
  const postSpy = jest.spyOn(ApiUtils, 'post').mockImplementation();
  const getLastKnownConfigMock = jest.spyOn(HueConfig, 'getLastKnownConfig');

  beforeEach(() => {
    windowSpy = jest.spyOn(window, 'window', 'get');
  });

  afterEach(() => {
    windowSpy.mockRestore();
    postSpy.mockReset();
    getLastKnownConfigMock.mockReset();
  });

  it('should log to console if dev mode, collect_usage and hueDebugAnalytics are true', () => {
    const consoleSpy = jest.spyOn(console, 'info').mockImplementation();
    getLastKnownConfigMock.mockImplementation(() => {
      return { hue_config: { collect_usage: true } };
    });

    windowSpy.mockImplementation(() => ({
      DEV: true,
      hueDebugAnalytics: true
    }));

    hueAnalytics.log('area1', 'action1');

    expect(consoleSpy).toHaveBeenCalledWith(
      'Analytics debug:',
      'event',
      'area1',
      expect.objectContaining({
        action: 'action1'
      })
    );
  });

  it('should always log to backend if prioritised', () => {
    const isPrio = true;

    windowSpy.mockImplementation(() => ({}));

    hueAnalytics.log('area1', 'action1', isPrio);

    expect(postSpy).toHaveBeenCalledWith('/desktop/log_analytics', {
      action: 'action1',
      area: 'area1'
    });
  });

  it('should log to google analytics if COLLECT_USAGE is true but not in dev mode', () => {
    const gtagSpy = jest.fn();
    getLastKnownConfigMock.mockImplementation(() => {
      return { hue_config: { collect_usage: true } };
    });

    windowSpy.mockImplementation(() => ({
      DEV: false,
      gtag: gtagSpy
    }));

    hueAnalytics.log('area1', 'action1');

    expect(gtagSpy).toHaveBeenCalledWith(
      'event',
      'area1',
      expect.objectContaining({
        action: 'action1'
      })
    );
  });

  it('should always log to backend when convert is used', () => {
    windowSpy.mockImplementation(() => ({}));

    hueAnalytics.convert('area1', 'action1');

    expect(postSpy).toHaveBeenCalledWith('/desktop/log_analytics', {
      action: 'action1',
      area: 'area1'
    });
  });

  it('should use global listener to log clicks on element with attribute "data-hue-analytics"', () => {
    const gtagSpy = jest.fn();
    getLastKnownConfigMock.mockImplementation(() => {
      return { hue_config: { collect_usage: true } };
    });
    windowSpy.mockImplementation(() => ({
      DEV: false,
      gtag: gtagSpy
    }));

    let globallyAddedEventListener!: EventListener;
    jest.spyOn(document, 'addEventListener').mockImplementationOnce((eventType, listenerToTest) => {
      globallyAddedEventListener = listenerToTest as EventListener;
    });

    setupGlobalListenersForAnalytics();

    const button = document.createElement('button');
    button.dataset.hueAnalytics = 'test-area:testbutton click';
    const myEvent = new Event('click');
    Object.defineProperty(myEvent, 'target', { writable: false, value: button });

    globallyAddedEventListener(myEvent);

    expect(gtagSpy).toHaveBeenCalledWith(
      'event',
      'test-area',
      expect.objectContaining({
        action: 'testbutton click'
      })
    );
  });

  it('should use global listener and backend API to log clicks on element with attribute "data-hue-analytics-prio"', () => {
    windowSpy.mockImplementation(() => ({}));

    let globallyAddedEventListener!: EventListener;
    jest.spyOn(document, 'addEventListener').mockImplementationOnce((eventType, listenerToTest) => {
      globallyAddedEventListener = listenerToTest as EventListener;
    });

    setupGlobalListenersForAnalytics();

    const button = document.createElement('button');
    button.dataset.hueAnalytics = 'test-area:testbutton click';
    button.dataset.hueAnalyticsPrio = 'true';
    const myEvent = new Event('click');
    Object.defineProperty(myEvent, 'target', { writable: false, value: button });

    globallyAddedEventListener(myEvent);

    expect(postSpy).toHaveBeenCalledWith('/desktop/log_analytics', {
      action: 'testbutton click',
      area: 'test-area'
    });
  });
});
