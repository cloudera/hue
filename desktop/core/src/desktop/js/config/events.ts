import { HueConfig } from './types';

export const REFRESH_CONFIG_TOPIC = 'cluster.config.refresh.config';
export const CONFIG_REFRESHED_TOPIC = 'cluster.config.set.config';
export type ConfigRefreshedEvent = HueConfig | undefined;

export const GET_KNOWN_CONFIG_TOPIC = 'cluster.config.get.config';
export type GetKnownConfigEvent = (appConfig?: HueConfig) => void;
