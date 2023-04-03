import { renderHook } from '@testing-library/react';

import i18next from 'i18next';
import HttpApi from 'i18next-http-backend';
import { initReactI18next } from 'react-i18next';

// Since the our i18nReact is globally mocked in jest.init.js
// we need to use requireActual when testing the actual i18nReact module
const { i18nReact } = jest.requireActual('./i18nReact');

describe('i18nReact', () => {
  const originalHueLang = global.HUE_LANG;
  jest.mock('i18next');

  // Setup mocks used to initialize i18next
  const initMock = jest.fn();
  const useInitReactI18nextMock = jest.fn().mockReturnValue({ init: initMock });
  const useHttpApiMock = jest
    .spyOn(i18next, 'use')
    .mockReturnValue({ ...i18next, use: useInitReactI18nextMock });

  const renderUseTranslationHook = () => {
    // Since we mock the i18next init calls we have to pass an instance to
    // i18nReact.useTranslation here in order to supress a console warning.
    return renderHook(() => i18nReact.useTranslation('translations', { i18n: i18next }));
  };

  afterEach(() => {
    global.HUE_LANG = originalHueLang;
    initMock.mockClear();
  });

  it('initializes i18next with HttpApi and initReactI18next once the useTranslation hook is used', () => {
    expect(useHttpApiMock).not.toHaveBeenCalled();
    expect(useInitReactI18nextMock).not.toHaveBeenCalled();

    renderUseTranslationHook();
    expect(useHttpApiMock).toHaveBeenCalledWith(HttpApi);
    expect(useInitReactI18nextMock).toHaveBeenCalledWith(initReactI18next);
  });

  it('initializes i18next with language defined in global var HUE_LANG', () => {
    global.HUE_LANG = 'en-us';
    renderUseTranslationHook();
    expect(initMock).toHaveBeenCalledWith(expect.objectContaining({ lng: global.HUE_LANG }));
  });

  it('initializes i18next with fallback language "en"', () => {
    global.HUE_LANG = undefined;
    renderUseTranslationHook();
    expect(initMock).toHaveBeenCalledWith(expect.objectContaining({ fallbackLng: 'en' }));
  });

  it('initializes i18next with load strategy "languageOnly" if full locale is NOT supported', () => {
    global.HUE_LANG = 'en-us';
    const testConfig = { ...i18nReact.getI18nConfig(), supportedLngs: ['en'] };
    const getI18nConfigMock = jest.spyOn(i18nReact, 'getI18nConfig').mockReturnValue(testConfig);

    renderUseTranslationHook();
    expect(initMock).toHaveBeenCalledWith(expect.objectContaining({ lng: 'en-us' }));
    expect(initMock).toHaveBeenCalledWith(expect.objectContaining({ load: 'languageOnly' }));

    getI18nConfigMock.mockRestore();
  });

  it('initializes i18next with load strategy "currentOnly" if full locale is supported', () => {
    global.HUE_LANG = 'pt-BR';
    const testConfig = { ...i18nReact.getI18nConfig(), supportedLngs: ['pt-BR'] };
    const getI18nConfigMock = jest.spyOn(i18nReact, 'getI18nConfig').mockReturnValue(testConfig);

    renderUseTranslationHook();
    expect(initMock).toHaveBeenCalledWith(expect.objectContaining({ lng: 'pt-BR' }));
    expect(initMock).toHaveBeenCalledWith(expect.objectContaining({ load: 'currentOnly' }));
    getI18nConfigMock.mockRestore();
  });
});
