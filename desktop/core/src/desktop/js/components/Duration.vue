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

<template>
  <span>{{ duration }}</span>
</template>

<script lang="ts">
  import { defineComponent } from 'vue';

  import { Duration as LuxonDuration, DurationUnit } from 'luxon';
  import I18n from '../utils/i18n';

  const SHORT_LIMITS = [
    { unit: <DurationUnit>'years', postfix: 'year', appendS: true },
    { unit: <DurationUnit>'days', postfix: 'day', appendS: true },
    { unit: <DurationUnit>'hours', postfix: 'h', appendS: false },
    { unit: <DurationUnit>'minutes', postfix: 'm', appendS: false },
    { unit: <DurationUnit>'seconds', postfix: 's', appendS: false },
    { unit: <DurationUnit>'milliseconds', postfix: 'ms', appendS: false }
  ];

  export const duration = (value: number, short?: boolean): string => {
    const luxonDuration = LuxonDuration.fromMillis(value);
    if (short) {
      for (const limit of SHORT_LIMITS) {
        const val = Math.floor(luxonDuration.as(limit.unit));
        if (val >= 1) {
          return val + I18n(limit.postfix + (limit.appendS && val > 1 ? 's' : ''));
        }
      }
      return `0${I18n('ms')}`;
    }
    return luxonDuration.toFormat('hh:mm:ss');
  };

  export default defineComponent({
    props: {
      value: {
        type: Number,
        required: true
      },
      short: Boolean
    },

    computed: {
      duration(): string {
        return duration(this.value, this.short);
      }
    }
  });
</script>

<style lang="scss" scoped></style>
