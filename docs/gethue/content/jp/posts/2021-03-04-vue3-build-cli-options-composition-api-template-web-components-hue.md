---
title: Vue 3 の紹介と Hue クエリエディタでの Web コンポーネント
author: Hue Team
type: post
date: 2021-03-04T00:00:00+00:00
url: /blog/vue3-build-cli-options-composition-api-template-web-components-hue
sf_thumbnail_type:
  - none
sf_thumbnail_link_type:
  - link_to_post
sf_detail_type:
  - none
sf_page_title:
  - 1
sf_page_title_style:
  - standard
sf_no_breadcrumbs:
  - 1
sf_page_title_bg:
  - none
sf_page_title_text_style:
  - light
sf_background_image_size:
  - cover
sf_social_sharing:
  - 1
sf_related_articles:
  - 1
sf_sidebar_config:
  - left-sidebar
sf_left_sidebar:
  - Sidebar-2
sf_right_sidebar:
  - Sidebar-1
sf_caption_position:
  - caption-right
sf_remove_promo_bar:
  - 1
ampforwp-amp-on-off:
  - default
categories:
  - Version 4.10
  - Development

---

Hue プロジェクトは 10 年以上の長い歴史があります。この間、私たちが使用していた技術の中にはかなり古くなったものもあります。そのため、Hue の改善点を検討する際、UI 技術のアップグレードが最優先されました。

Hue は[Mako](https://www.makotemplates.org/) と [Knockout JS](https://knockoutjs.com/) ライブラリを組み合わせて全ての UI を作成しています。現時点では新しいライブラリの方が生産性が高いため、最新のベストを探すことにしました。私たちの目標は次の通りです:
- 最新の UI ライブラリを導入し、将来的に Knockout JS を置き換える
- [コンポーネント](https://docs.gethue.com/developer/components/) をパッケージ化し、さまざまなプロジェクトで共有する
- 部分的なサーバーサイドレンダリングから完全なクライアントサイドのレンダリングに移行
- コードの品質を高めるため Typescript の導入

[React](https://reactjs.org/) と [Vue](https://vuejs.org/) が最有力候補でした。[Angular](https://angularjs.org) と [Svelte](https://svelte.dev) も候補に挙がっていました。何度からブレインストーミングを行った結果、Vue.js を採用することにしました。どのフレームワークも動的なインターフェイスを書くための生産的な方法を提供していますが、Vue はさしでがましくなく、 非常に高速で小さく、そして最も重要なことに、私たちの現在の[コンポーネント化](https://docs.gethue.com/developer/components)の取り組みに良く適合していたので Vue が選ばれました。最初は Vue 2 を使っていましたが、すぐに Vue 3 がリリースされたので、代わりに Vue 3 を使用することに決めました。移行する前にいくつかの質問に答える必要がありました。
- Vue のビルドプロセスをどのようにセットアップするか？
- 最適なコンポーネント構文は何か？
- Web コンポーネントとしてパッケージ化する方法は？

## ビルドプロセス

Hue では UI のビルドに webpack を使用していました。コンポーネントを徐々にアップグレードしていく計画だったので、古い UI のコードと新しい UI のコードの両方で動作するセットアップが必要でした。幸運なことに、Vue CLI によって作成された boilerplate プロジェクトは、内部で webpack を使用していることがわかりました。そこで CLI を使ってダミープロジェクトを作成し、依存関係や設定をコピーすることにしました。

ダミープロジェクトの作成はとても簡単でした。`npm install -g @vue/cli` を使用して CLI をインストールし、`vue create hue-dummy` でプロジェクトを作成します。作成中、プロジェクトのプリセットではなくプロジェクトの機能を手動で選択することにし、以下のように Vue Version, Babel, Typescript, CSS Preprocessor, Linter & Unit Tests を選択しました。

    Vue CLI v4.5.11
    ? Please pick a preset: Manually select features
    ? Check the features needed for your project:
    ◉ Choose Vue version
    ◉ Babel
    ◉ TypeScript
    ◯ Progressive Web App (PWA) Support
    ◯ Router
    ◯ Vuex
    ◉ CSS Pre-processors
    ◉ Linter / Formatter
    ❯◉ Unit Testing
    ◯ E2E Testing

続くページでは、Vue 3, Typescript, SASS, Prettier, Lint, Jest および CLI でダミープロジェクトの作成を開始しました。

    Vue CLI v4.5.11
    ? Please pick a preset: Manually select features
    ? Check the features needed for your project: Choose Vue version, Babel, TS, CSS Pre-processors, Linter, Unit
    ? Choose a version of Vue.js that you want to start the project with 3.x (Preview)
    ? Use class-style component syntax? No
    ? Use Babel alongside TypeScript (required for modern mode, auto-detected polyfills, transpiling JSX)? Yes
    ? Pick a CSS pre-processor (PostCSS, Autoprefixer and CSS Modules are supported by default): Sass/SCSS (with node-sass)
    ? Pick a linter / formatter config: Prettier
    ? Pick additional lint features: Lint on save
    ? Pick a unit testing solution: Jest
    ? Where do you prefer placing config for Babel, ESLint, etc.? In dedicated config files
    ? Save this as a preset for future projects? (y/N) N

プロジェクトが作成されたら `package.json` と Babel, ESLint などの設定ファイルの差分をとり、変更点をコピーして依存関係を更新しました。`webpack.config.js`, `vue-loader` および `babel-loader` ルールは .vue と .ts ファイルに対してそれぞれ置き、ビルドが開始されました。

_注意: デモプロジェクトで問題になった設定の一つは`tsconfig.json` での `"jsx":"preserve"` でした。これは`<>` スタイルのタイプキャストと競合していました。Vue のテンプレートではなく JSX を使用したい場合は、型キャストに `as` キーワードを使うようにしてください。_

## コンポーネントの構文、API、テンプレート

プロジェクトが Vue と Typescript の機能を使ってビルドを開始したので、次の課題は、記述スタイル、ひいてはコンポーネントがどのように見えるのかを把握することでした。Vue はコンポーネントのさまざまな記述方法をサポートしています。

### クラス形式の構文

クラス形式の構文では、コンポーネントを ES6 のクラスとして定義します。コンポーネントのデータ、メソッド、およびその他のプロパティはデコレータでアノテートできます。また、継承やミックスインなどの、オブジェクト指向プログラミング(OOP)の機能の利用も容易になります。**Vue Class Component** は、Vue のコンポーネントをクラススタイルの構文で作成することができるライブラリです。Typescript と並んで、これは最もオブジェクト指向的なアプローチに見えました。しかし、**追加のライブラリに依存することになる**ため、他の方法を検討することにしました。さらに、これは次のセクションで説明するオプション API の構文上の補完に過ぎません。

以下は、コンポーネントをクラス形式で表現したものです。

    import Vue from 'vue'
    import Component from 'vue-class-component'

    @Component
    export default class Counter extends Vue {
      // Class definition
    }

### オブジェクト形式の構文とオプション API

オブジェクト形式では、コンポーネントを `options object` として定義します。コンポーネントのデータ、メソッド、プロパティは、オプションオブジェクトの子として定義されます。また、コンポーネントのライフサイクルの作ステージで呼び出される関数を追加することもできます。Vue では、これらをライフサイクルフックと呼んでいます。古エッらのオブジェクトのフォーマットとフックのシグネチャは、Vue オプション API で定義されています。Vue 3 が提供するネイティブな Typescript のサポートとともに、オブジェクトの形式は良好でした。しかし、Vue 3 はそれだけではありません！

以下は、オブジェクト形式でコンポーネントを定義する方法です。

    import { defineComponent } from 'vue';

    export default defineComponent({
      // Options object definition
    });

### Composition API

[Composition API](https://v3.vuejs.org/guide/composition-api-introduction.html) は、Vue 3 が提供する、コンポーネントを作成するための新しい方法です。この方法では、`setup function` を使用して、完全なコンポーネントが構成されます。メソッドはネスト化されたクロージャー関数として定義され、リアクティブなデータメンバーは返却されるオブジェクトの子として返すことができます。onMounted のような特別な関数は、ライフサイクルフックを定義するために提供されます。

以下は、オブジェクト形式でコンポーネントを定義する方法です。

    import { defineComponent, onMounted } from 'vue';

    defineComponent(() => {
      return {
        data: 1
      };
    });

### 私たちのコンポーネントテンプレート

最終的にはオブジェクト形式の構文を採用し、オプションとコンポジション API を組み合わせて、セットアップフックがセットアップ関数として機能するようにしました。**プロップやコンポーネントのような静的なアイテムを定義するのはオプション API で簡単にでき、reactive provide と inject のような動的なアイテムを定義するのはコンポジション API で簡単にできるので、組み合わせて使うことにしました。さらに、多くの Vue 3 のドキュメントの多くがこの形式を使用しています。** さまざまな資料を調べた結果、コンポーネントとして以下のようなテンプレートを作成しました。このテンプレートには、コンポーネントを定義するために使用できるさまざまなオプション(コンポーネント、ディレクティブ、プロップなど)が用意されており、使用する順番、各パーツがどのように相互作用するかなどが記載されています。このテンプレートは全てのコンポーネントのベースになります。

    <template>
      <Comp1 @click="onClick">Click Me!</Comp1>
    </template>

    <script lang="ts">
      import { defineComponent, PropType, inject, provide } from 'vue';

      import Comp1 from './Comp1.vue';
      import AnotherComp2 from './Comp2.vue';

      export default <T, K>() => defineComponent({
        components: {
          Comp1,
          AnotherComp2
        },

        directives: {
          'overflow-on-hover': overflowOnHover
        },

        provide(): {
          hideDrawer: () => void;
        } {
          return {
            hideDrawer: (): void => {
              this.$emit('close');
            }
          };
        },

        props: {
          propA: Boolean,
          propB: {
            type: String,
            default: 'Abc'
          },
          items: {
            type: Object as PropType<SidebarNavigationItem[]>,
            required: true
          }
        },

        emits: ['emitted-event-name'],

        setup(props): { // Setup function for composition
          const injectedReactiveValue: Type = inject('injectedReactiveValue');

          return {
            dataMember: false,
            processedProp: !props.propA,
            injectedReactiveValue
          }
        },

        data(): {
          return {
              genericMember: null as <T | null>
          };
        },

        computed: {
          isActive(): Boolean { // Computed getter
            // Statements
          }
        },

        mounted(): void {
          // Statements
        },
        unmounted(): void {
          // Statements
        },

        methods: {
          onClick(event: Event): void {
            console.log(this.processedProp);
          }
        },

        watch: {
          items(): void { // Watches items prop
            // Statements to be executed
          }
        },
        created() {
          this.$watch(
            ():K => this.foo.bar, // Watch nested property bar of type K
            (val:K, prevVal:K): void => {
              // Statements to be executed
            }
          )
        }
      })
    </script>

## Web コンポーネント

次の目標は、さまざまなプロジェクトで共有できるように、コンポーネントをパッケージ化することでした。現代の Web UI はさまざまな技術で構築されているため、フレームワークにとらわれない方法が必要でした。そこで登場したのが Web コンポーネントです。Web コンポーネントを使うと再利用可能なカスタム要素を作成し、その機能を他のコードから分離してカプセル化することができます。

しかし驚いたことに、コンポーネントを Web コンポーネントに変換するための公式の Vue パッケージは Vue 3をサポートしていませんでした。また、[この問題](https://github.com/vuejs/vue-web-component-wrapper/issues/93)については、サポートが追加されるにはしばらく時間がかかりそうです。そこで代替手段を見つけなければなりませんでした。私たちは、Vue 3で動作する Vue 2 Web コンポーネントのラッパーの移植版を開発しました。名称は `vue3-webcomponent-wrapper` です。コードは[こちら](https://github.com/cloudera/hue/tree/master/desktop/core/src/desktop/js/vue/wrapper)で、npm パッケージは[こちら](https://www.npmjs.com/package/vue3-webcomponent-wrapper)から利用可能です。私たちの移植版では、リアクティブな属性、イベントとスロットをサポートしています。

_注: 公式のラッパーのアップグレードを妨げる主な要因の一つは、Vue 3のビルドツールにshadow-root CSS インジェクションがないことでした。Hueではシャドウがなくても大丈夫だったので、これは問題ではなく、移植にはほとんど1日もかかりませんでした。_

コンポーネントラッパーの使い方はとても簡単です。`npm i --save vue3-webcomponent-wrapper` でインストールできます。インストールが完了したら、次のような `my-component` という名前のカスタムタグを作成する方法を以下のスニペットで紹介します。

Vue 2 と [@vuejs/vue-web-component-wrapper](https://github.com/vuejs/vue-web-component-wrapper) を使用する前の状態です。

    import Vue from 'vue'
    import wrapper from '@vue/web-component-wrapper'
    import MyComponent from "./components/MyComponent.vue";

    const CustomElement = wrapper(Vue, MyComponent)
    window.customElements.define('my-component', CustomElement)

Vue 3 と vue3-webcomponent-wrapper を使用した場合です。

    import { createApp, h } from "vue";
    import wrapper from "vue3-webcomponent-wrapper";
    import MyComponent from "./components/MyComponent.vue";

    const CustomElement = wrapper(MyComponent, createApp, h);
    window.customElements.define("my-component", CustomElement);

ラッパーの詳細については、こちらの[デモアプリ](https://github.com/sreenaths/vue3-webcomponent-wrapper-demo)でご確認ください。また、[この](https://github.com/cloudera/hue/blob/master/apps/metastore/src/metastore/templates/metastore.mako#L825) er-diagram タグは Hue プロジェクトでのラッパーの使用例です。

### 公式の Vue 3 Web コンポーネントラッパーを使用する

公式のラッパーは私たちの実装とよく似ているはずです。とはいえ、公式ラッパーの正確な関数シグネチャは現時点では不明です。今後のアップデートのために[このページ](https://www.npmjs.com/package/vue3-webcomponent-wrapper)をチェックしておいてください。

## 以上で完成です！

Hue は、Vue 3とコンポーネントラッパーを使用して、かなり古い技術の仕様から Web インターフェース開発の最前線へと移行しました。私たちは、コンポーネントプログラミングは分離して簡単に共有できるため、非常に効率的な開発パラダイムであると強く信じています。次のエピソードでは、新しい Hue 5 の API との統合について説明する予定です。

~ Sreenath from the Hue Team
