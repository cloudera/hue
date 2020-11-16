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
  <div
    v-if="visible"
    v-click-outside="clickOutside"
    class="hue-ace-autocompleter"
    :style="{ top: top + 'px', left: left + 'px' }"
  >
    <div class="autocompleter-suggestions">
      <div
        v-if="autocompleteResults.availableCategories.length > 1 || autocompleteResults.loading"
        class="autocompleter-header"
      >
        <!-- ko if: suggestions.availableCategories().length > 1 -->
        <div
          v-if="autocompleteResults.availableCategories.length > 1"
          class="autocompleter-categories"
        >
          <div
            v-for="category in autocompleteResults.availableCategories"
            :key="category.label"
            :style="{
              'border-color':
                autocompleteResults.activeCategory === category ? category.color : 'transparent'
            }"
            :class="{ active: autocompleteResults.activeCategory === category }"
            @click="categoryClick(category, $event)"
          >
            {{ category.label }}
          </div>
        </div>
        <div class="autocompleter-spinner">
          <spinner :spin="autocompleteResults.loading" size="small" />
        </div>
      </div>
      <div class="autocompleter-entries">
        <div>
          <div
            v-for="(suggestion, index) in autocompleteResults.filtered"
            :key="suggestion.category.label + suggestion.value"
            class="autocompleter-suggestion"
            :class="{ selected: index === selectedIndex }"
            @click="clickToInsert(index)"
            @mouseover="hoveredIndex = index"
            @mouseout="hoveredIndex = null"
          >
            <div class="autocompleter-suggestion-value">
              <div
                class="autocompleter-dot"
                :style="{ 'background-color': suggestion.category.color }"
              />
              <matched-text :suggestion="suggestion" :filter="autocompleteResults.filter" />
              <i v-if="suggestion.details && suggestion.details.primary_key" class="fa fa-key" />
            </div>
            <div class="autocompleter-suggestion-meta">
              <i v-if="suggestion.popular" class="fa fa-star-o popular-color" />
              <span>{{ suggestion.meta }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
  import MatchedText from 'apps/notebook2/components/aceEditor/autocomplete/MatchedText.vue';
  import Executor from 'apps/notebook2/execution/executor';
  import { clickOutsideDirective } from 'components/directives/clickOutsideDirective';
  import Spinner from 'components/Spinner.vue';
  import SubscriptionTracker from 'components/utils/SubscriptionTracker';
  import { Ace } from 'ext/ace';
  import ace from 'ext/aceHelper';
  import SqlAutocompleter from './SqlAutocompleter';
  import { defer } from 'utils/hueUtils';
  import { Prop } from 'vue-property-decorator';
  import AutocompleteResults, { Category } from './AutocompleteResults';
  import Vue from 'vue';
  import Component from 'vue-class-component';

  import I18n from 'utils/i18n';

  const aceUtil = <Ace.AceUtil>ace.require('ace/autocomplete/util');
  const HashHandler: typeof Ace.HashHandler = ace.require('ace/keyboard/hash_handler').HashHandler;

  @Component({
    components: { MatchedText, Spinner },
    methods: { I18n },
    directives: {
      'click-outside': clickOutsideDirective
    }
  })
  export default class AceAutocomplete extends Vue {
    @Prop({ required: true })
    executor!: Executor;
    @Prop({ required: true })
    editorId!: string;
    @Prop({ required: true })
    editor!: Ace.Editor;
    @Prop({ required: false, default: false })
    temporaryOnly?: boolean;

    active = false;
    left = 0;
    top = 0;
    selectedIndex: number | null = null;
    hoveredIndex: number | null = null;
    base: Ace.Anchor | null = null;

    autocompleter?: SqlAutocompleter;
    autocompleteResults?: AutocompleteResults;

    changeTimeout = -1;
    positionInterval = -1;
    keyboardHandler: Ace.HashHandler | null = null;

    changeListener: (() => void) | null = null;
    mousedownListener = this.detach.bind(this);
    mousewheelListener = this.detach.bind(this);

    subTracker = new SubscriptionTracker();

    // TODO: Move filter, filtered, categories, activeCategory from AutocompleteResults to this component

    created(): void {
      this.keyboardHandler = new HashHandler();
      this.registerKeybindings(this.keyboardHandler);

      this.changeListener = () => {
        window.clearTimeout(this.changeTimeout);
        const cursor = this.editor.selection.lead;
        if (this.base && (cursor.row !== this.base.row || cursor.column < this.base.column)) {
          this.detach();
        } else {
          this.changeTimeout = window.setTimeout(() => {
            if (!this.autocompleteResults || !this.base) {
              return;
            }
            const pos = this.editor.getCursorPosition();
            if (this.active && this.autocompleter && this.autocompleter.onPartial) {
              this.autocompleter.onPartial(
                aceUtil.retrievePrecedingIdentifier(
                  this.editor.session.getLine(pos.row),
                  pos.column
                )
              );
            }
            this.autocompleteResults.filter = this.editor.session.getTextRange({
              start: this.base,
              end: pos
            });

            this.positionAutocompleteDropdown();

            // TODO: Vue does not react on changes to autocompleteResults.filter could be because we initialize it
            // in mounted
            this.$forceUpdate();

            if (!this.autocompleteResults.filtered.length) {
              this.detach();
            }
          }, 200);
        }
      };
    }

    registerKeybindings(keyboardHandler: Ace.HashHandler): void {
      keyboardHandler.bindKeys({
        Up: () => {
          if (!this.autocompleteResults) {
            return;
          }
          if (this.autocompleteResults.filtered.length <= 1) {
            this.detach();
            this.editor.execCommand('golineup');
          } else if (this.selectedIndex) {
            this.selectedIndex = this.selectedIndex - 1;
            this.hoveredIndex = null;
            this.scrollSelectionIntoView();
          } else {
            this.selectedIndex = this.autocompleteResults.filtered.length - 1;
            this.hoveredIndex = null;
            this.scrollSelectionIntoView();
          }
        },
        Down: () => {
          if (!this.autocompleteResults) {
            return;
          }
          if (this.autocompleteResults.filtered.length <= 1) {
            this.detach();
            this.editor.execCommand('golinedown');
          } else if (
            this.selectedIndex !== null &&
            this.selectedIndex < this.autocompleteResults.filtered.length - 1
          ) {
            this.selectedIndex = this.selectedIndex + 1;
            this.hoveredIndex = null;
            this.scrollSelectionIntoView();
          } else {
            this.selectedIndex = 0;
            this.hoveredIndex = null;
            this.scrollSelectionIntoView();
          }
        },
        'Ctrl-Up|Ctrl-Home': () => {
          if (!this.autocompleteResults) {
            return;
          }
          if (this.autocompleteResults.filtered.length <= 1) {
            this.detach();
            this.editor.execCommand('gotostart');
          } else {
            this.selectedIndex = 0;
            this.hoveredIndex = null;
            this.scrollSelectionIntoView();
          }
        },
        'Ctrl-Down|Ctrl-End': () => {
          if (!this.autocompleteResults) {
            return;
          }
          if (this.autocompleteResults.filtered.length <= 1) {
            this.detach();
            this.editor.execCommand('gotoend');
          } else if (this.autocompleteResults.filtered.length > 0) {
            this.selectedIndex = this.autocompleteResults.filtered.length - 1;
            this.hoveredIndex = null;
            this.scrollSelectionIntoView();
          }
        },
        Esc: () => {
          this.detach();
        },
        Return: () => {
          this.insertSuggestion(() => {
            this.editor.execCommand('insertstring', '\n');
          });
        },
        'Shift-Return': () => {
          // TODO: Delete suffix
          this.insertSuggestion();
        },
        Tab: () => {
          this.insertSuggestion(() => {
            this.editor.execCommand('indent');
          });
        }
      });
    }

    clickToInsert(index: number): void {
      this.selectedIndex = index;
      this.insertSuggestion();
      this.editor.focus();
    }

    insertSuggestion(emptyCallback?: () => void): void {
      if (!this.autocompleteResults) {
        return;
      }

      const results = this.autocompleteResults;

      if (this.selectedIndex === null || !results.filtered.length) {
        this.detach();
        if (emptyCallback) {
          emptyCallback();
        }
        return;
      }

      const selectedSuggestion = results.filtered[this.selectedIndex];
      const valueToInsert = selectedSuggestion.value;

      // Not always the case as we also match in comments
      if (valueToInsert.toLowerCase() === results.filter.toLowerCase()) {
        // Close the autocomplete when the user has typed a complete suggestion
        this.detach();
        return;
      }

      if (results.filter) {
        const ranges = this.editor.selection.getAllRanges();
        ranges.forEach(range => {
          range.start.column -= results.filter.length;
          this.editor.session.remove(range);
        });
      }

      // TODO: Move cursor handling for '? FROM tbl' here
      this.editor.execCommand('insertstring', valueToInsert);
      this.editor.renderer.scrollCursorIntoView();
      this.detach();
    }

    mounted(): void {
      this.autocompleter = new SqlAutocompleter({
        editorId: this.editorId,
        executor: this.executor,
        editor: this.editor,
        temporaryOnly: this.temporaryOnly
      });

      this.subTracker.addDisposable(this.autocompleter);

      this.autocompleteResults = this.autocompleter.autocompleteResults;

      this.subTracker.subscribe('hue.ace.autocompleter.done', () => {
        defer(() => {
          if (
            this.active &&
            (!this.autocompleteResults ||
              ((!this.autocompleteResults.filtered || !this.autocompleteResults.filtered.length) &&
                !this.autocompleteResults.loading))
          ) {
            this.detach();
          }
        });
      });

      this.subTracker.subscribe(
        'hue.ace.autocompleter.show',
        async (details: {
          editor: Ace.Editor;
          lineHeight: number;
          position: { top: number; left: number };
        }) => {
          if (details.editor !== this.editor || !this.autocompleter) {
            return;
          }
          const session = this.editor.getSession();
          const pos = this.editor.getCursorPosition();
          const line = session.getLine(pos.row);
          const prefix = aceUtil.retrievePrecedingIdentifier(line, pos.column);
          const newBase = session.doc.createAnchor(pos.row, pos.column - prefix.length);

          this.positionAutocompleteDropdown();

          const afterAutocomplete = () => {
            newBase.$insertRight = true;
            this.base = newBase;
            if (this.autocompleteResults) {
              this.autocompleteResults.filter = prefix;
            }
            this.active = true;
            this.selectedIndex = 0;
          };

          if (
            !this.active ||
            !this.base ||
            newBase.column !== this.base.column ||
            newBase.row !== this.base.row
          ) {
            try {
              await this.autocompleter.autocomplete();
              afterAutocomplete();
              this.attach();
            } catch (err) {
              afterAutocomplete();
            }
          } else {
            afterAutocomplete();
          }
        }
      );
    }

    positionAutocompleteDropdown(): void {
      const renderer = this.editor.renderer;
      const newPos = renderer.$cursorLayer.getPixelPosition(undefined, true);
      const rect = this.editor.container.getBoundingClientRect();
      const lineHeight = renderer.layerConfig.lineHeight;
      this.top = newPos.top + rect.top - renderer.layerConfig.offset + lineHeight + 3;
      this.left = newPos.left + rect.left - renderer.scrollLeft + renderer.gutterWidth;
    }

    get visible(): boolean {
      return (
        this.active &&
        !!(
          this.autocompleteResults &&
          (this.autocompleteResults.loading || this.autocompleteResults.filtered.length)
        )
      );
    }

    scrollSelectionIntoView(): void {
      // TODO: implement
    }

    suggestionSelected(index: number): void {
      this.selectedIndex = index;
      //$parent.insertSuggestion(); $parent.editor().focus();
    }

    attach(): void {
      this.disposeEventHandlers();

      if (this.keyboardHandler) {
        this.editor.keyBinding.addKeyboardHandler(this.keyboardHandler);
      }
      if (this.changeListener) {
        this.editor.on('changeSelection', this.changeListener);
      }
      this.editor.on('mousedown', this.mousedownListener);
      this.editor.on('mousewheel', this.mousewheelListener);

      let currentOffset = {
        top: this.editor.container.offsetTop,
        left: this.editor.container.offsetLeft
      };
      let currentPixelRatio = window.devicePixelRatio; // Detect zoom changes

      this.positionInterval = window.setInterval(() => {
        const newOffset = {
          top: this.editor.container.offsetTop,
          left: this.editor.container.offsetLeft
        };
        if (currentPixelRatio !== window.devicePixelRatio) {
          currentOffset = newOffset;
          currentPixelRatio = window.devicePixelRatio;
        } else if (
          Math.abs(newOffset.top - currentOffset.top) > 20 ||
          Math.abs(newOffset.left - currentOffset.left) > 20
        ) {
          this.detach();
        }
      }, 300);
    }

    categoryClick(category: Category, event: Event): void {
      if (!this.autocompleteResults) {
        return;
      }
      this.autocompleteResults.activeCategory = category;

      // TODO: Why doesn't Vue reactivity pick up the change?
      this.$forceUpdate();

      event.stopPropagation();
      this.editor.focus();
    }

    clickOutside(): void {
      if (this.active) {
        this.detach();
      }
    }

    disposeEventHandlers(): void {
      window.clearTimeout(this.changeTimeout);
      window.clearInterval(this.positionInterval);
      if (this.keyboardHandler) {
        this.editor.keyBinding.removeKeyboardHandler(this.keyboardHandler);
      }
      if (this.changeListener) {
        this.editor.off('changeSelection', this.changeListener);
      }
      this.editor.off('mousedown', this.mousedownListener);
      this.editor.off('mousewheel', this.mousewheelListener);
    }

    detach(): void {
      if (!this.autocompleteResults) {
        return;
      }
      this.autocompleteResults.cancelRequests();
      this.disposeEventHandlers();
      if (!this.active) {
        return;
      }
      this.active = false;
      if (this.base) {
        this.base.detach();
        this.base = null;
      }
    }

    destroyed(): void {
      this.disposeEventHandlers();
      this.subTracker.dispose();
    }
  }
</script>

<style lang="scss" scoped></style>
