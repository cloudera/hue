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
  <teleport v-if="!alreadyPresentInDom" to="body">
    <div id="hueIconSprites">
      <svg version="1.1" xmlns="http://www.w3.org/2000/svg" style="display: none;">
        <defs>
          <symbol id="hueDatabaseSymbol" viewBox="0 0 24 24">
            <g stroke="none" stroke-width="1" fill="none" fill-rule="evenodd">
              <g id="system-icons/database" fill="#000000">
                <path
                  id="database"
                  d="M18.2129,9.4307 C15.2589,10.8937 8.7409,10.8937 5.7869,9.4307 L5.7869,6.3377 C7.4619,6.9907 9.7359,7.3067 11.9999,7.3067 C14.2639,7.3067 16.5379,6.9907 18.2129,6.3377 L18.2129,9.4307 Z M18.2129,14.3707 C15.2589,15.8337 8.7409,15.8337 5.7869,14.3707 L5.7869,11.0407 C7.4619,11.6837 9.7359,11.9997 11.9999,11.9997 C14.2639,11.9997 16.5379,11.6837 18.2129,11.0407 L18.2129,14.3707 Z M18.2129,18.9167 C18.2129,19.3227 16.1019,20.2807 11.9999,20.2807 C7.8989,20.2807 5.7869,19.3227 5.7869,18.9167 L5.7869,15.9827 C7.4619,16.6237 9.7359,16.9407 11.9999,16.9407 C14.2639,16.9407 16.5379,16.6237 18.2129,15.9827 L18.2129,18.9167 Z M11.9999,3.7197 C14.4439,3.7197 17.0759,4.0947 17.9999,4.8357 C15.0249,6.1697 8.9539,6.1697 5.9899,4.8267 C6.9239,4.0947 8.6399,3.7197 11.9999,3.7197 L11.9999,3.7197 Z M11.9999,1.9997 C10.6599,1.9997 3.9999,2.1487 3.9999,5.0827 L3.9999,18.9167 C3.9999,19.6977 4.4969,20.7547 6.8729,21.4167 C8.2339,21.7917 10.0609,21.9997 11.9999,21.9997 C13.3399,21.9997 19.9999,21.8517 19.9999,18.9167 L19.9999,5.0827 C19.9999,2.1487 13.3399,1.9997 11.9999,1.9997 L11.9999,1.9997 Z"
                />
              </g>
            </g>
          </symbol>

          <symbol id="hueSpinnerLarge" viewBox="0 0 64 64">
            <path
              stroke-width="4"
              fill="none"
              stroke="currentColor"
              fill-rule="evenodd"
              d="M56,32 C56,45.256 45.256,56 32,56 C18.744,56 8,45.256 8,32 C8,18.744 18.744,8 32,8"
            />
          </symbol>

          <symbol id="hueSpinnerSmall" viewBox="0 0 24 24">
            <path
              stroke-width="1"
              fill="none"
              stroke="currentColor"
              fill-rule="evenodd"
              d="M21,12 C21,16.971 16.971,21 12,21 C7.029,21 3,16.971 3,12 C3,7.029 7.029,3 12,3"
            />
          </symbol>
        </defs>
      </svg>
    </div>
  </teleport>
</template>

<script lang="ts">
  import { defineComponent } from 'vue';

  import './HueIcons.scss';

  export default defineComponent({
    name: 'HueIcons',
    setup() {
      const alreadyPresentInDom = !!document.getElementById('hueIconSprites');
      return { alreadyPresentInDom };
    }
  });
</script>
