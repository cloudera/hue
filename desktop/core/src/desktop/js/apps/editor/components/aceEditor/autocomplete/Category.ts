// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import { Suggestion } from './AutocompleteResults';
import I18n from 'utils/i18n';

export interface CategoryInfo {
  categoryId: CategoryId;
  color: string;
  detailsComponent?: string;
  label: string;
  popular?: boolean;
  weight?: number;
}

enum Colors {
  Column = '#2fae2f',
  Database = '#517989',
  Files = '#9e1414',
  IdentCteVar = '#ca4f01',
  Keyword = '#0074d2',
  Popular = '#61bbff',
  Sample = '#fea7a7',
  Table = '#ffa139',
  UDF = '#acfbac'
}

export enum CategoryId {
  All = 'All',
  ColRefKeyword = 'ColRefKeyword',
  Column = 'Column',
  CTE = 'CTE',
  Database = 'Database',
  Files = 'Files',
  Identifier = 'Identifier',
  Keyword = 'Keyword',
  Option = 'Option',
  Popular = 'Popular',
  PopularActiveJoin = 'PopularActiveJoin',
  PopularAggregate = 'PopularAggregate',
  PopularFilter = 'PopularFilter',
  PopularGroupBy = 'PopularGroupBy',
  PopularJoin = 'PopularJoin',
  PopularJoinCondition = 'PopularJoinCondition',
  PopularOrderBy = 'PopularOrderBy',
  Sample = 'Sample',
  Table = 'Table',
  UDF = 'UDF',
  Variable = 'Variable',
  VirtualColumn = 'VirtualColumn'
}

export const Category: { [categoryId in keyof typeof CategoryId]: CategoryInfo } = {
  All: {
    categoryId: CategoryId.All, // TODO: used?
    color: '#90ceff',
    label: I18n('All')
  },
  ColRefKeyword: {
    categoryId: CategoryId.ColRefKeyword,
    color: Colors.Keyword,
    label: I18n('Keywords'),
    weight: 100
  },
  Column: {
    categoryId: CategoryId.Column,
    color: Colors.Column,
    label: I18n('Columns'),
    weight: 1000
  },
  CTE: {
    categoryId: CategoryId.CTE,
    color: Colors.IdentCteVar,
    label: I18n('CTEs'),
    weight: 700
  },
  Database: {
    categoryId: CategoryId.Database,
    color: Colors.Database,
    label: I18n('Databases'),
    weight: 500
  },
  Files: {
    categoryId: CategoryId.Files,
    color: Colors.Files,
    label: I18n('Files'),
    weight: 300
  },
  Identifier: {
    categoryId: CategoryId.Identifier,
    color: Colors.IdentCteVar,
    label: I18n('Identifiers'),
    weight: 800
  },
  Keyword: {
    categoryId: CategoryId.Keyword,
    color: Colors.Keyword,
    label: I18n('Keywords'),
    weight: 0
  },
  Option: {
    categoryId: CategoryId.Option,
    color: Colors.UDF,
    detailsComponent: 'OptionDetailsPanel',
    label: I18n('Options'),
    weight: 400
  },
  Popular: {
    categoryId: CategoryId.Popular,
    color: Colors.Popular,
    label: I18n('Popular'),
    popular: true
  },
  PopularAggregate: {
    categoryId: CategoryId.PopularAggregate,
    color: Colors.Popular,
    detailsComponent: 'PopularAggregateUdfPanel',
    label: I18n('Popular'),
    popular: true,
    weight: 1500
  },
  PopularActiveJoin: {
    categoryId: CategoryId.PopularActiveJoin,
    color: Colors.Popular,
    label: I18n('Popular'),
    detailsComponent: 'PopularDetailsPanel',
    popular: true,
    weight: 1500
  },
  PopularFilter: {
    categoryId: CategoryId.PopularFilter,
    color: Colors.Popular,
    label: I18n('Popular'),
    detailsComponent: 'PopularDetailsPanel',
    popular: true,
    weight: 1400
  },
  PopularGroupBy: {
    categoryId: CategoryId.PopularGroupBy,
    color: Colors.Popular,
    detailsComponent: 'PopularDetailsPanel',
    label: I18n('Popular'),
    popular: true,
    weight: 1300
  },
  PopularJoin: {
    categoryId: CategoryId.PopularJoin,
    color: Colors.Popular,
    detailsComponent: 'PopularDetailsPanel',
    label: I18n('Popular'),
    weight: 1500
  },
  PopularJoinCondition: {
    categoryId: CategoryId.PopularJoinCondition,
    color: Colors.Popular,
    detailsComponent: 'PopularDetailsPanel',
    label: I18n('Popular'),
    popular: true,
    weight: 1500
  },
  PopularOrderBy: {
    categoryId: CategoryId.PopularOrderBy,
    color: Colors.Popular,
    detailsComponent: 'PopularDetailsPanel',
    label: I18n('Popular'),
    popular: true,
    weight: 1200
  },
  Sample: {
    categoryId: CategoryId.Sample,
    color: Colors.Sample,
    label: I18n('Samples'),
    weight: 900
  },
  Table: {
    categoryId: CategoryId.Table,
    color: Colors.Table,
    label: I18n('Tables'),
    weight: 600
  },
  UDF: {
    categoryId: CategoryId.UDF,
    detailsComponent: 'UdfDetailsPanel',
    color: Colors.UDF,
    label: I18n('UDFs'),
    weight: 400
  },
  Variable: {
    categoryId: CategoryId.Variable,
    color: Colors.IdentCteVar,
    label: I18n('Variables'),
    weight: 50
  },
  VirtualColumn: {
    categoryId: CategoryId.VirtualColumn,
    color: Colors.Column,
    label: I18n('Columns'),
    weight: 200
  }
};

export const extractCategories = (suggestions: Suggestion[]): CategoryInfo[] => {
  const uniqueCategories = new Set<CategoryInfo>();
  suggestions.forEach(suggestion => {
    if (suggestion.popular) {
      uniqueCategories.add(Category.Popular);
    } else if (
      suggestion.category.categoryId === CategoryId.Table ||
      suggestion.category.categoryId === CategoryId.Column ||
      suggestion.category.categoryId === CategoryId.UDF
    ) {
      uniqueCategories.add(Category[suggestion.category.categoryId]);
    }
  });
  const categories: CategoryInfo[] = [...uniqueCategories];
  categories.sort((a, b) => a.label.localeCompare(b.label));
  categories.unshift(Category.All);
  return categories;
};
