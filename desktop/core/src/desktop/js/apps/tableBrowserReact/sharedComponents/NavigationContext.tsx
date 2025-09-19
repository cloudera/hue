// Licensed to Cloudera, Inc. under one or more contributor license agreements.
// Apache License 2.0 applies.

import React, { createContext, useContext } from 'react';

export interface NavigationAPI {
  navigateToSources: () => void;
  navigateToSource: (sourceType: string) => void;
  navigateToDatabase: (database: string) => void;
  navigateToTable: (database: string, table: string) => void;
  navigateToColumn: (database: string, table: string, column: string) => void;
  navigateToField: (database: string, table: string, column: string, fields: string[]) => void;
}

const noop = () => {};

const defaultApi: NavigationAPI = {
  navigateToSources: noop,
  navigateToSource: noop,
  navigateToDatabase: noop,
  navigateToTable: noop as unknown as (db: string, t: string) => void,
  navigateToColumn: noop as unknown as (db: string, t: string, c: string) => void,
  navigateToField: noop as unknown as (db: string, t: string, c: string, f: string[]) => void
};

const NavigationContext = createContext<NavigationAPI>(defaultApi);

export const useNavigation = (): NavigationAPI => useContext(NavigationContext);

export const NavigationProvider = ({
  value,
  children
}: {
  value: NavigationAPI;
  children: React.ReactNode;
}): JSX.Element => {
  return <NavigationContext.Provider value={value}>{children}</NavigationContext.Provider>;
};

export default NavigationContext;
