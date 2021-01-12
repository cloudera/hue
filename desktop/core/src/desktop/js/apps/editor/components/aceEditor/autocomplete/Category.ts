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
  label: string;
  weight?: number;
  popular?: boolean;
}

enum Colors {
  Popular = '#61bbff',
  Keyword = '#0074d2',
  Column = '#2fae2f',
  Table = '#ffa139',
  Database = '#517989',
  Sample = '#fea7a7',
  IdentCteVar = '#ca4f01',
  UDF = '#acfbac',
  Files = '#9e1414'
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
  Popular: {
    categoryId: CategoryId.Popular,
    color: Colors.Popular,
    label: I18n('Popular'),
    popular: true
  },
  PopularAggregate: {
    categoryId: CategoryId.PopularAggregate,
    weight: 1500,
    color: Colors.Popular,
    label: I18n('Popular'),
    popular: true
  },
  PopularGroupBy: {
    categoryId: CategoryId.PopularGroupBy,
    weight: 1300,
    color: Colors.Popular,
    label: I18n('Popular'),
    popular: true
  },
  PopularOrderBy: {
    categoryId: CategoryId.PopularOrderBy,
    weight: 1200,
    color: Colors.Popular,
    label: I18n('Popular'),
    popular: true
  },
  PopularFilter: {
    categoryId: CategoryId.PopularFilter,
    weight: 1400,
    color: Colors.Popular,
    label: I18n('Popular'),
    popular: true
  },
  PopularActiveJoin: {
    categoryId: CategoryId.PopularActiveJoin,
    weight: 1500,
    color: Colors.Popular,
    label: I18n('Popular'),
    popular: true
  },
  PopularJoinCondition: {
    categoryId: CategoryId.PopularJoinCondition,
    weight: 1500,
    color: Colors.Popular,
    label: I18n('Popular'),
    popular: true
  },
  Column: {
    categoryId: CategoryId.Column,
    weight: 1000,
    color: Colors.Column,
    label: I18n('Columns')
  },
  Sample: {
    categoryId: CategoryId.Sample,
    weight: 900,
    color: Colors.Sample,
    label: I18n('Samples')
  },
  Identifier: {
    categoryId: CategoryId.Identifier,
    weight: 800,
    color: Colors.IdentCteVar,
    label: I18n('Identifiers')
  },
  CTE: {
    categoryId: CategoryId.CTE,
    weight: 700,
    color: Colors.IdentCteVar,
    label: I18n('CTEs')
  },
  Table: {
    categoryId: CategoryId.Table,
    weight: 600,
    color: Colors.Table,
    label: I18n('Tables')
  },
  Database: {
    categoryId: CategoryId.Database,
    weight: 500,
    color: Colors.Database,
    label: I18n('Databases')
  },
  UDF: {
    categoryId: CategoryId.UDF,
    weight: 400,
    color: Colors.UDF,
    label: I18n('UDFs')
  },
  Option: {
    categoryId: CategoryId.Option,
    weight: 400,
    color: Colors.UDF,
    label: I18n('Options')
  },
  Files: {
    categoryId: CategoryId.Files,
    weight: 300,
    color: Colors.Files,
    label: I18n('Files')
  },
  VirtualColumn: {
    categoryId: CategoryId.VirtualColumn,
    weight: 200,
    color: Colors.Column,
    label: I18n('Columns')
  },
  ColRefKeyword: {
    categoryId: CategoryId.ColRefKeyword,
    weight: 100,
    color: Colors.Keyword,
    label: I18n('Keywords')
  },
  Variable: {
    categoryId: CategoryId.Variable,
    weight: 50,
    color: Colors.IdentCteVar,
    label: I18n('Variables')
  },
  Keyword: {
    categoryId: CategoryId.Keyword,
    weight: 0,
    color: Colors.Keyword,
    label: I18n('Keywords')
  },
  PopularJoin: {
    categoryId: CategoryId.PopularJoin,
    weight: 1500,
    color: Colors.Popular,
    label: I18n('Popular')
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
