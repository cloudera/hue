/*
 *
 * HORTONWORKS DATAPLANE SERVICE AND ITS CONSTITUENT SERVICES
 *
 * (c) 2016-2018 Hortonworks, Inc. All rights reserved.
 *
 * This code is provided to you pursuant to your written agreement with Hortonworks, which may be the terms of the
 * Affero General Public License version 3 (AGPLv3), or pursuant to a written agreement with a third party authorized
 * to distribute this code.  If you do not have a written agreement with Hortonworks or with an authorized and
 * properly licensed third party, you do not have any rights to this code.
 *
 * If this code is provided to you under the terms of the AGPLv3:
 * (A) HORTONWORKS PROVIDES THIS CODE TO YOU WITHOUT WARRANTIES OF ANY KIND;
 * (B) HORTONWORKS DISCLAIMS ANY AND ALL EXPRESS AND IMPLIED WARRANTIES WITH RESPECT TO THIS CODE, INCLUDING BUT NOT
 *   LIMITED TO IMPLIED WARRANTIES OF TITLE, NON-INFRINGEMENT, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE;
 * (C) HORTONWORKS IS NOT LIABLE TO YOU, AND WILL NOT DEFEND, INDEMNIFY, OR HOLD YOU HARMLESS FOR ANY CLAIMS ARISING
 *   FROM OR RELATED TO THE CODE; AND
 * (D) WITH RESPECT TO YOUR EXERCISE OF ANY RIGHTS GRANTED TO YOU FOR THE CODE, HORTONWORKS IS NOT LIABLE FOR ANY
 *   DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, PUNITIVE OR CONSEQUENTIAL DAMAGES INCLUDING, BUT NOT LIMITED TO,
 *   DAMAGES RELATED TO LOST REVENUE, LOST PROFITS, LOSS OF INCOME, LOSS OF BUSINESS ADVANTAGE OR UNAVAILABILITY,
 *   OR LOSS OR CORRUPTION OF DATA.
 *
 */

import Ember from 'ember';

const GAINFO = [
   Ember.Object.create({
       name: 'WAREHOUSES',
       info: '/warehouses'
   }),
   Ember.Object.create({
       name: 'DATABASES',
       info: '/database'
   }),
   Ember.Object.create({
       name: 'DATABASE_DROP',
       info: '/database/drop'
   }),
   Ember.Object.create({
       name: 'DATABASE_CREATE',
       info: '/database/create'
   }),
   Ember.Object.create({
       name: 'TABLES',
       info: '/tables'
   }),
   Ember.Object.create({
       name: 'TABLE_CREATE',
       info: '/table/create'
   }),
   Ember.Object.create({
       name: 'TABLE_RENAME',
       info: '/table/rename'
   }),
   Ember.Object.create({
       name: 'TABLE_DELETE',
       info: '/table/rename'
   }),
   Ember.Object.create({
       name: 'COMPOSE',
       info: '/compose'
   }),
   Ember.Object.create({
       name: 'SAVEDQUERIES',
       info: '/savedQueries'
   }),
   Ember.Object.create({
       name: 'SAVEDQUERIES_CREATE',
       info: '/savedQueries/create'
   }),
   Ember.Object.create({
       name: 'SAVEDQUERIES_DELETE',
       info: '/savedqueries/delete'
   }),
   Ember.Object.create({
       name: 'QUERY_DETAILS',
       info: '/querydetails'
   }),
   Ember.Object.create({
       name: 'REPORTS',
       info: '/reports'
   }),
   Ember.Object.create({
       name: 'REPORTS_RW',
       info: '/reports/rw'
   }),
   Ember.Object.create({
       name: 'REPORTS_JOIN',
       info: '/reports/join'
   }),
   Ember.Object.create({
       name: 'SETTINGS',
       info: '/manage'
   }),
   Ember.Object.create({
       name: 'SETTINGS_CREATE',
       info: '/settings/create'
   }),
   Ember.Object.create({
       name: 'SETTINGS_DELETE',
       info: '/settings/delete'
   }),
   Ember.Object.create({
       name: 'SETTINGS_EDIT',
       info: '/settings/edit'
   }),
   Ember.Object.create({
       name: 'QUERY_DIFF',
       info: '/query-diff'
   })
];

export default GAINFO;