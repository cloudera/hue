export const setWebCompProp = <T extends HTMLElement>(el: Element | null | undefined, propName: keyof T, data: any) => {
  if (el) {
    if (data) {
      el.setAttribute(String(propName), '');
      (el as T)[propName] = data;
    } else {
      el.removeAttribute(String(propName));
      delete((el as T)[propName]);
    }
  }
}