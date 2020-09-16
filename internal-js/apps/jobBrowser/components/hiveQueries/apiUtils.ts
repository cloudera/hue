import {Facet, FieldInfo, Query, Search, SearchMeta, SearchRequest} from './index';

export const fetchSuggestedSearches = async (options: { entityType: string }): Promise<{ searches: Search[] }> => {
  // TODO: Implement GET 'api/suggested-searches?entityType=x'
  return { searches: [] };
}

export const fetchFacets = async (options: {
  startTime: number;
  endTime: number;
  facetFields: string;
}): Promise<{ facets: Facet[], rangeFacets: unknown[] }> => {
  // TODO: Implement GET '/api/query/facets?startTime=x&endTime=y&facetFields=z'
  return { facets: [], rangeFacets: [] };
}

export const fetchFieldsInfo = async (): Promise<{ fieldsInfo: FieldInfo[] }> => {
 // TODO: Implement GET '/api/query/fields-information'
 return { fieldsInfo: [] }
}

export const search = async (options: SearchRequest): Promise<{ meta: SearchMeta; queries: Query[] }> => {
  // TODO: Implement POST '/api/query/search' ({ search: options } in body)
  return { meta: { limit: 0, offset: 0, size:0 }, queries: [] }
}
