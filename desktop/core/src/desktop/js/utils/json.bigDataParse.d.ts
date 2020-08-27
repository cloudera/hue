interface JSON {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  bigdataParse(text: string, reviver?: (this: any, key: string, value: any) => any): any;
}
