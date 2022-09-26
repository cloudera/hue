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
      <svg version="1.1" xmlns="http://www.w3.org/2000/svg" style="display: none">
        <defs>
          <symbol id="hueChevronLeftSymbol" viewBox="0 0 24 24">
            <path d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z" />
          </symbol>

          <symbol id="hueChevronLeftLimitSymbol" viewBox="0 0 24 24">
            <path d="M18.41 16.59L13.82 12l4.59-4.59L17 6l-6 6 6 6zM6 6h2v12H6z" />
          </symbol>

          <symbol id="hueChevronRightSymbol" viewBox="0 0 24 24">
            <path d="M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z" />
          </symbol>

          <symbol id="hueChevronRightLimitSymbol" viewBox="0 0 24 24">
            <path d="M5.59 7.41L10.18 12l-4.59 4.59L7 18l6-6-6-6zM16 6h2v12h-2z" />
          </symbol>

          <symbol id="hueColumnSymbol" viewBox="0 0 24 24">
            <!-- "View Column" from Google Fonts, Apache 2.0 license -->
            <path d="M0 0h24v24H0V0z" fill="none" />
            <path d="M4 5v13h17V5H4zm10 2v9h-3V7h3zM6 7h3v9H6V7zm13 9h-3V7h3v9z" />
          </symbol>

          <symbol id="hueConnectorSymbol" viewBox="0 0 24 24">
            <!-- "Storage" from Google Fonts, Apache 2.0 license -->
            <path d="M0 0h24v24H0V0z" fill="none" />
            <path
              d="M2 20h20v-4H2v4zm2-3h2v2H4v-2zM2 4v4h20V4H2zm4 3H4V5h2v2zm-4 7h20v-4H2v4zm2-3h2v2H4v-2z"
            />
          </symbol>

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

          <symbol id="hueDropDownSymbol" viewBox="0 0 24 24">
            <polygon points="6 9 12 15 18 9" />
          </symbol>

          <symbol id="hueDropLeftSymbol" viewBox="0 0 24 24">
            <polygon points="15 6 9 11.9988 15 18" />
          </symbol>

          <symbol id="hueDropRightSymbol" viewBox="0 0 24 24">
            <polygon points="9 6 9 18 15 11.9988" />
          </symbol>

          <symbol id="hueDropUpSymbol" viewBox="0 0 24 24">
            <polygon points="12.0001 9 6 15.0001 17.999 15.0001" />
          </symbol>

          <symbol id="hueSpinnerLargeSymbol" viewBox="0 0 64 64">
            <path
              stroke-width="4"
              fill="none"
              stroke="currentColor"
              fill-rule="evenodd"
              d="M56,32 C56,45.256 45.256,56 32,56 C18.744,56 8,45.256 8,32 C8,18.744 18.744,8 32,8"
            />
          </symbol>

          <symbol id="hueSpinnerSmallSymbol" viewBox="0 0 24 24">
            <path
              stroke-width="1"
              fill="none"
              stroke="currentColor"
              fill-rule="evenodd"
              d="M21,12 C21,16.971 16.971,21 12,21 C7.029,21 3,16.971 3,12 C3,7.029 7.029,3 12,3"
            />
          </symbol>

          <symbol id="hueTableSymbol" viewBox="0 0 16 16">
            <g transform="scale(0.875) translate(1,1)">
              <path
                d="M18.349 2H5.634C4.728 2 4 2.728 4 3.634v12.732C4 17.272 4.728 18 5.634 18h12.732c.906 0 1.634-.728 1.634-1.634V3.634C19.982 2.728 19.254 2 18.349 2zm-12.715.941h12.732c.373 0 .693.302.693.693V5.25H4.94V3.634c0-.39.302-.693.693-.693zM9.86 13.134v-3.036h4.12v3.036H9.86zm4.12.941v2.984H9.86v-2.984h4.12zm0-7.902v3.001H9.86v-3h4.12zM8.919 9.174H4.941v-3H8.92v3zm0 .924v3.036H4.941v-3.036H8.92zm5.984 0h4.138v3.036h-4.138v-3.036zm0-.924v-3h4.138v3h-4.138zM4.941 16.35v-2.274H8.92v2.984H5.634c-.39-.018-.693-.32-.693-.71zm13.408.692h-3.446v-2.966h4.138v2.291c0 .373-.302.675-.692.675z"
                transform="translate(-57 -261) translate(0 31) translate(53 228)"
              />
            </g>
          </symbol>

          <symbol id="hueViewSymbol" viewBox="0 0 24 24">
            <path
              d="M12,5 C18,5 22,12.5 22,12.5 C22,12.5 17,20 12,20 C7,20 2,12.5 2,12.5 C2,12.5 6,5 12,5 Z M12,7 C8.496,7 5.633,10.59 4.408,12.41 C6.055,14.53 9.313,18 12,18 C14.688,18 17.948,14.526 19.596,12.406 C18.378,10.585 15.532,7 12,7 Z M12,8 C14.209,8 16,9.791 16,12 C16,14.209 14.209,16 12,16 C9.791,16 8,14.209 8,12 C8,10.984 8.391,10.068 9.014,9.363 C9.01,9.408 9,9.453 9,9.5 C9,10.328 9.671,11 10.5,11 C11.329,11 12,10.328 12,9.5 C12,8.877 11.62,8.344 11.08,8.116 C11.376,8.047 11.682,8 12,8 Z"
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
