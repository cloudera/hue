import {Facet, FieldInfo, Query, Search, SearchMeta, SearchRequest} from './index';

export const fetchSuggestedSearches = async (options: { entityType: string }): Promise<Search[]> => {
  // TODO: Implement GET 'api/suggested-searches?entityType=x'
  const response = { searches: [] };
  return response.searches;
}

export const fetchFacets = async (options: {
  startTime: number;
  endTime: number;
  facetFields: string;
}): Promise<{ facets: Facet[], rangeFacets: unknown[] }> => {
  // TODO: Implement GET '/api/query/facets?startTime=x&endTime=y&facetFields=z'
  return { facets: [], rangeFacets: [] };
}

export const fetchFieldsInfo = async (): Promise<FieldInfo[]> => {
  // TODO: Implement GET '/api/query/fields-information'
  const response = { fieldsInfo: [] };
  return response.fieldsInfo;
}

export const search = async (options: SearchRequest): Promise<{ meta: SearchMeta; queries: Query[] }> => {
  // TODO: Implement POST '/api/query/search' ({ search: options } in body)
  return { meta: { limit: 0, offset: 0, size:0 }, queries: [] }
}

export const deleteSearch = async (search: Search): Promise<void> => {
  // TODO: Implement POST ...
}

export const saveSearch = async (options: {
  name: string;
  category: string;
  type: string;
  entity: string;
  clause: string;
}): Promise<void> => {
  // TODO: Implement POST ...
}
