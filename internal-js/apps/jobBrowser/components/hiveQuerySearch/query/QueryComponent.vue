<!--
  Licensed to Cloudera, Inc. under one
  or more contributor license agreements.  See the NOTICE file
  distributed with this work for additional information
  regarding copyright ownership.  Cloudera, Inc. licenses this file
  to you under the Apache License, Version 2.0 (the
  "License"); you may not use this file except in compliance
  with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
-->

<script lang="ts">
import Vue from 'vue';
import Component from 'vue-class-component';
import { Prop } from 'vue-property-decorator';
import HueTable, { Column, Row } from '../../common/HueTable.vue';
import { QueryModel } from '../index';

@Component
export default class QueryComponent extends Vue {
  @Prop({ required: false })
  queryModels: QueryModel[] = [];
  @Prop({ required: false })
  queryModel?: QueryModel;

  constructor() {
    super();

    // TODO: Does queryModel change for this component?
    if (this.queryModel) {
      this.queryModels.push(this.queryModel);
    }
  }

  numberToLetter(value: number): string {
    return String.fromCharCode(65 + value);  // A, B, C, ...
  }
}
</script>
