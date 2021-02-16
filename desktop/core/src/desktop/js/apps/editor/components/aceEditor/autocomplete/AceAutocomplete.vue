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
      <div v-if="availableCategories.length > 1 || loading" class="autocompleter-header">
        <!-- ko if: suggestions.availableCategories().length > 1 -->
        <div v-if="availableCategories.length > 1" class="autocompleter-categories">
          <div
            v-for="category in availableCategories"
            :key="category.label"
            :style="{
              'border-color':
                activeCategory.categoryId === category.categoryId ? category.color : 'transparent'
            }"
            :class="{ active: activeCategory.categoryId === category.categoryId }"
            @click="clickCategory(category, $event)"
          >
            {{ category.label }}
          </div>
        </div>
        <div class="autocompleter-spinner">
          <spinner :spin="loading" size="small" />
        </div>
      </div>
      <div ref="entriesScrollDiv" class="autocompleter-entries">
        <div ref="entriesDiv">
          <div
            v-for="(suggestion, index) in filtered"
            :key="
              filter + activeCategory.categoryId + suggestion.category.categoryId + suggestion.value
            "
            class="autocompleter-suggestion"
            :class="{ selected: index === selectedIndex }"
            @click="clickSuggestion(index)"
            @mouseover="hoveredIndex = index"
            @mouseout="hoveredIndex = null"
          >
            <div class="autocompleter-suggestion-value">
              <div
                class="autocompleter-dot"
                :style="{ 'background-color': suggestion.category.color }"
              />
              <matched-text :suggestion="suggestion" :filter="filter" />
              <i
                v-if="suggestion.details && suggestion.details.hasOwnProperty('primary_key')"
                class="fa fa-key"
              />
            </div>
            <div class="autocompleter-suggestion-meta">
              <i v-if="suggestion.popular" class="fa fa-star-o popular-color" />
              <span>{{ suggestion.meta }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div v-if="detailsComponent" class="autocompleter-details">
      <component :is="detailsComponent" :suggestion="focusedEntry" :connector="connector" />
    </div>
  </div>
</template>

<script lang="ts">
  import { defineComponent, PropType } from 'vue';

  import { Ace } from 'ext/ace';
  import ace from 'ext/aceHelper';
  import { AutocompleteParser } from 'parse/types';
  import { Connector } from 'types/config';

  import { Category, CategoryId, CategoryInfo, extractCategories } from './Category';
  import Executor from 'apps/editor/execution/executor';
  import SubscriptionTracker from 'components/utils/SubscriptionTracker';
  import sqlUtils, { SortOverride } from 'sql/sqlUtils';
  import huePubSub from 'utils/huePubSub';
  import I18n from 'utils/i18n';

  import { Suggestion } from './AutocompleteResults';
  import MatchedText from './MatchedText.vue';
  import SqlAutocompleter from './SqlAutocompleter';
  import CatalogEntryDetailsPanel from './details/CatalogEntryDetailsPanel.vue';
  import OptionDetailsPanel from './details/OptionDetailsPanel.vue';
  import PopularAggregateUdfPanel from './details/PopularAggregateUdfPanel.vue';
  import PopularDetailsPanel from './details/PopularDetailsPanel.vue';
  import UdfDetailsPanel from './details/UdfDetailsPanel.vue';
  import Spinner from 'components/Spinner.vue';
  import { clickOutsideDirective } from 'components/directives/clickOutsideDirective';
  import { SqlReferenceProvider } from 'sql/reference/types';
  import hueDebug from 'utils/hueDebug';

  const aceUtil = <Ace.AceUtil>ace.require('ace/autocomplete/util');
  const HashHandler = <typeof Ace.HashHandler>ace.require('ace/keyboard/hash_handler').HashHandler;
  const REFRESH_STATEMENT_LOCATIONS_EVENT = 'editor.refresh.statement.locations';

  export default defineComponent({
    components: {
      CatalogEntryDetailsPanel,
      MatchedText,
      OptionDetailsPanel,
      PopularAggregateUdfPanel,
      PopularDetailsPanel,
      Spinner,
      UdfDetailsPanel
    },
    directives: {
      'click-outside': clickOutsideDirective
    },
    props: {
      autocompleteParser: {
        type: Object as PropType<AutocompleteParser>,
        required: true
      },
      sqlReferenceProvider: {
        type: Object as PropType<SqlReferenceProvider>,
        required: true
      },
      editor: {
        type: Object as PropType<Ace.Editor>,
        required: true
      },
      editorId: {
        type: String,
        required: true
      },
      executor: {
        type: Object as PropType<Executor>,
        required: true
      },
      temporaryOnly: {
        type: Boolean,
        required: false,
        default: false
      }
    },
    setup(props) {
      const subTracker = new SubscriptionTracker();

      const autocompleter = new SqlAutocompleter({
        editorId: props.editorId,
        executor: props.executor,
        editor: props.editor,
        temporaryOnly: props.temporaryOnly,
        autocompleteParser: props.autocompleteParser,
        sqlReferenceProvider: props.sqlReferenceProvider
      });

      const autocompleteResults = autocompleter.autocompleteResults;

      subTracker.addDisposable(autocompleter);

      return { subTracker, autocompleter, autocompleteResults };
    },
    data(component) {
      return {
        startLayout: null as DOMRect | null,
        startPixelRatio: window.devicePixelRatio,
        left: 0,
        top: 0,

        loading: false,
        active: false,
        filter: '',
        activeCategory: Category.All,
        selectedIndex: null as number | null,
        hoveredIndex: null as number | null,
        base: null as Ace.Anchor | null,
        sortOverride: null as SortOverride | null,
        suggestions: [] as Suggestion[],

        reTriggerTimeout: -1,
        changeTimeout: -1,
        positionInterval: -1,
        keyboardHandler: null as Ace.HashHandler | null,
        changeListener: null as (() => void) | null,

        mousedownListener: component.detach.bind(component),
        mousewheelListener: component.closeOnScroll.bind(component)
      };
    },
    computed: {
      connector(): Connector | undefined {
        if (this.executor) {
          return this.executor.connector();
        }
        return undefined;
      },

      detailsComponent(): string | undefined {
        if (this.focusedEntry && this.focusedEntry.details) {
          if (this.focusedEntry.hasCatalogEntry) {
            return 'CatalogEntryDetailsPanel';
          }
          return this.focusedEntry.category.detailsComponent;
        }
        return undefined;
      },
      availableCategories(): CategoryInfo[] {
        return extractCategories(this.suggestions);
      },
      filtered(): Suggestion[] {
        if (!this.autocompleteResults) {
          return [];
        }

        let result = this.suggestions;

        if (this.filter) {
          result = sqlUtils.autocompleteFilter(this.filter, result);
          huePubSub.publish('hue.ace.autocompleter.match.updated');
        }

        const activeCategory = this.activeCategory;

        const categoriesCount = new Map<CategoryId, number>();
        result = result.filter(suggestion => {
          categoriesCount.set(
            suggestion.category.categoryId,
            (categoriesCount.get(suggestion.category.categoryId) || 0) + 1
          );
          if (
            activeCategory !== Category.Popular &&
            (categoriesCount.get(suggestion.category.categoryId) || 0) >= 10 &&
            suggestion.category.popular
          ) {
            return false;
          }
          return (
            activeCategory.categoryId === Category.All.categoryId ||
            activeCategory.categoryId === suggestion.category.categoryId ||
            (activeCategory.categoryId === Category.Popular.categoryId && suggestion.popular)
          );
        });

        sqlUtils.sortSuggestions(result, this.filter, this.sortOverride);
        // eslint-disable-next-line vue/no-side-effects-in-computed-properties
        this.sortOverride = null;
        return result;
      },

      focusedEntry(): Suggestion | undefined {
        if (this.filtered.length) {
          if (this.hoveredIndex !== null) {
            return this.filtered[this.hoveredIndex];
          } else if (this.selectedIndex !== null) {
            return this.filtered[this.selectedIndex];
          }
        }
        return undefined;
      },

      visible(): boolean {
        return this.active && (this.loading || !!this.filtered.length);
      }
    },
    watch: {
      filter(): void {
        if (this.selectedIndex !== null) {
          this.selectedIndex = 0;
          const scrollDiv = <HTMLDivElement | undefined>this.$refs.entriesScrollDiv;
          if (scrollDiv) {
            scrollDiv.scrollTop = 0;
          }
        }
      },
      availableCategories(categories): void {
        if (categories.indexOf(this.activeCategory) === -1) {
          this.activeCategory = categories[0];
        }
      }
    },
    created(): void {
      this.keyboardHandler = new HashHandler();
      this.registerKeybindings(this.keyboardHandler);

      this.changeListener = () => {
        if (!this.autocompleteResults) {
          return;
        }
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
            this.updateFilter();
            this.positionAutocompleteDropdown();

            if (!this.filtered.length) {
              this.detach();
            }
          }, 200);
        }
      };
    },
    mounted(): void {
      const showAutocomplete = async () => {
        // The autocomplete can be triggered right after insertion of a suggestion
        // when live autocomplete is enabled, hence if already active we ignore.
        if (this.active || !this.autocompleter) {
          return;
        }
        const session = this.editor.getSession();
        const pos = this.editor.getCursorPosition();
        const line = session.getLine(pos.row);
        const prefix = aceUtil.retrievePrecedingIdentifier(line, pos.column);
        const newBase = session.doc.createAnchor(pos.row, pos.column - prefix.length);

        if (!this.base || newBase.column !== this.base.column || newBase.row !== this.base.row) {
          this.positionAutocompleteDropdown();
          try {
            this.loading = true;
            const parseResult = await this.autocompleter.autocomplete();
            if (hueDebug.showParseResult) {
              // eslint-disable-next-line no-restricted-syntax
              console.log(parseResult);
            }

            if (parseResult && this.autocompleteResults) {
              this.suggestions = [];
              this.autocompleteResults.update(parseResult, this.suggestions).finally(() => {
                this.loading = false;
              });

              this.selectedIndex = 0;
              newBase.$insertRight = true;
              this.base = newBase;
              if (this.autocompleteResults) {
                this.filter = prefix;
              }
              this.active = true;
              this.attach();
            }
          } catch (err) {
            if (typeof console.warn !== 'undefined') {
              console.warn(err);
            }
            this.detach();
          }
        }
      };

      this.editor.on('showAutocomplete', showAutocomplete);
      const onHideAutocomplete = this.detach.bind(this);
      this.editor.on('hideAutocomplete', onHideAutocomplete);
      this.subTracker.subscribe('hue.ace.autocompleter.hide', onHideAutocomplete);

      this.subTracker.addDisposable({
        dispose: () => {
          this.editor.off('showAutocomplete', showAutocomplete);
          this.editor.off('hideAutocomplete', onHideAutocomplete);
        }
      });

      this.subTracker.subscribe(
        'editor.autocomplete.temporary.sort.override',
        (sortOverride: SortOverride): void => {
          this.sortOverride = sortOverride;
        }
      );
    },

    unmounted(): void {
      this.disposeEventHandlers();
      this.subTracker.dispose();
    },

    methods: {
      I18n,

      clickCategory(category: CategoryInfo, event: Event): void {
        if (!this.autocompleteResults) {
          return;
        }
        this.activeCategory = category;

        event.stopPropagation();
        this.editor.focus();
      },

      clickOutside(): void {
        if (this.active) {
          this.detach();
        }
      },

      clickSuggestion(index: number): void {
        this.selectedIndex = index;
        this.insertSuggestion();
        this.editor.focus();
      },

      updateFilter(): void {
        if (this.base) {
          const pos = this.editor.getCursorPosition();
          this.filter = this.editor.session.getTextRange({
            start: this.base,
            end: pos
          });
        }
      },

      registerKeybindings(keyboardHandler: Ace.HashHandler): void {
        keyboardHandler.bindKeys({
          Up: () => {
            if (this.filtered.length <= 1) {
              this.detach();
              this.editor.execCommand('golineup');
            } else if (this.selectedIndex) {
              this.selectedIndex = this.selectedIndex - 1;
              this.hoveredIndex = null;
              this.scrollSelectionIntoView();
            } else {
              this.selectedIndex = this.filtered.length - 1;
              this.hoveredIndex = null;
              this.scrollSelectionIntoView();
            }
          },
          Down: () => {
            if (this.filtered.length <= 1) {
              this.detach();
              this.editor.execCommand('golinedown');
            } else if (
              this.selectedIndex !== null &&
              this.selectedIndex < this.filtered.length - 1
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
            if (this.filtered.length <= 1) {
              this.detach();
              this.editor.execCommand('gotostart');
            } else {
              this.selectedIndex = 0;
              this.hoveredIndex = null;
              this.scrollSelectionIntoView();
            }
          },
          'Ctrl-Down|Ctrl-End': () => {
            if (this.filtered.length <= 1) {
              this.detach();
              this.editor.execCommand('gotoend');
            } else if (this.filtered.length > 0) {
              this.selectedIndex = this.filtered.length - 1;
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
      },

      insertSuggestion(emptyCallback?: () => void): void {
        if (this.selectedIndex === null || !this.filtered.length) {
          this.detach();
          if (emptyCallback) {
            emptyCallback();
          }
          return;
        }

        const selectedSuggestion = this.filtered[this.selectedIndex];
        const valueToInsert = selectedSuggestion.value;

        // Not always the case as we also match in comments
        if (valueToInsert.toLowerCase() === this.filter.toLowerCase()) {
          // Close the autocomplete when the user has typed a complete suggestion
          this.detach();
          return;
        }

        if (this.filter) {
          const ranges = this.editor.selection.getAllRanges();
          ranges.forEach(range => {
            range.start.column -= this.filter.length;
            this.editor.session.remove(range);
          });
        }

        // TODO: Move cursor handling for '? FROM tbl' here
        this.editor.execCommand('insertstring', valueToInsert);
        this.editor.renderer.scrollCursorIntoView();
        this.detach();

        if (this.editor.getOption('enableLiveAutocompletion')) {
          if (/\S+\(\)$/.test(valueToInsert)) {
            this.editor.moveCursorTo(
              this.editor.getCursorPosition().row,
              this.editor.getCursorPosition().column - 1
            );
            return;
          }

          window.clearTimeout(this.reTriggerTimeout);
          this.reTriggerTimeout = window.setTimeout(() => {
            if (this.active) {
              return;
            }

            let reTrigger;
            if (/(\? from \S+[^.]\s*$)/i.test(valueToInsert)) {
              this.editor.moveCursorTo(
                this.editor.getCursorPosition().row,
                this.editor.getCursorPosition().column - (valueToInsert.length - 1)
              );
              this.editor.removeTextBeforeCursor(1);
              reTrigger = true;
            } else {
              reTrigger = /\.$/.test(valueToInsert);
            }

            if (reTrigger) {
              huePubSub.publish(REFRESH_STATEMENT_LOCATIONS_EVENT, this.editorId);
              window.setTimeout(() => {
                this.editor.execCommand('startAutocomplete');
              }, 1);
            }
          }, 400);
        }
      },

      positionAutocompleteDropdown(): void {
        const renderer = this.editor.renderer;
        const newPos = renderer.$cursorLayer.getPixelPosition(undefined, true);
        const rect = this.editor.container.getBoundingClientRect();
        const lineHeight = renderer.layerConfig.lineHeight;
        this.top = newPos.top + rect.top - renderer.layerConfig.offset + lineHeight + 3;
        this.left = newPos.left + rect.left - renderer.scrollLeft + renderer.gutterWidth;
      },

      scrollSelectionIntoView(): void {
        const scrollDiv = <HTMLDivElement | undefined>this.$refs.entriesScrollDiv;
        const entriesDiv = <HTMLDivElement | undefined>this.$refs.entriesDiv;
        if (
          !scrollDiv ||
          !entriesDiv ||
          this.selectedIndex === null ||
          entriesDiv.clientHeight < scrollDiv.clientHeight
        ) {
          return;
        }
        const entryHeight = entriesDiv.clientHeight / entriesDiv.childElementCount;
        const firstVisibleIndex = Math.ceil(scrollDiv.scrollTop / entryHeight);
        const visibleCount = scrollDiv.clientHeight / entryHeight;
        const lastVisibleIndex = firstVisibleIndex + visibleCount - 1;

        if (firstVisibleIndex <= this.selectedIndex && this.selectedIndex <= lastVisibleIndex) {
          return;
        }
        if (this.selectedIndex < firstVisibleIndex) {
          scrollDiv.scrollTop = this.selectedIndex * entryHeight;
        } else {
          scrollDiv.scrollTop = Math.round((this.selectedIndex - (visibleCount - 1)) * entryHeight);
        }
      },

      suggestionSelected(index: number): void {
        this.selectedIndex = index;
        this.insertSuggestion();
        this.editor.focus();
      },

      closeOnScroll(): void {
        if (!this.active || !this.startLayout) {
          return;
        }
        const newLayout = this.editor.container.getBoundingClientRect();
        const yDiff = newLayout.top - this.startLayout.top;
        const xDiff = newLayout.left - this.startLayout.left;
        if (this.startPixelRatio !== window.devicePixelRatio) {
          // Ignore zoom changes
          this.startLayout = newLayout;
        } else if (Math.abs(yDiff) > 10 || Math.abs(xDiff) > 10) {
          // Close if scroll more than 10px in any direction
          this.detach();
        }
      },

      attach(): void {
        this.updateFilter();
        this.disposeEventHandlers();

        this.startLayout = this.editor.container.getBoundingClientRect();
        this.startPixelRatio = window.devicePixelRatio;

        if (this.keyboardHandler) {
          this.editor.keyBinding.addKeyboardHandler(this.keyboardHandler);
        }
        if (this.changeListener) {
          this.editor.on('changeSelection', this.changeListener);
        }
        this.editor.on('mousedown', this.mousedownListener);
        this.editor.on('mousewheel', this.mousewheelListener);
        this.positionInterval = window.setInterval(this.closeOnScroll.bind(this), 300);
      },

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
      },

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
    }
  });
</script>
