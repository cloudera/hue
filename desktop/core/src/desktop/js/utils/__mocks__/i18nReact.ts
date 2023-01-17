import { UseTranslationOptions } from 'react-i18next';
interface useTranslationReturn {
  t(str: string): string;
  ready: boolean;
}
interface i18nReactMock {
  useTranslation(string, options?: UseTranslationOptions): useTranslationReturn;
}

export const i18nReact: i18nReactMock = {
  useTranslation: () => {
    return {
      t: str => str,
      ready: true
    };
  }
};
