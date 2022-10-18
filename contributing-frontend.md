![alt text](https://raw.githubusercontent.com/cloudera/hue/master/docs/images/hue_logo.png "Hue Logo")

Thank you for considering contributing to Hue!

# Contributing to Hue frontend
The Frontend in Hue is currently made up of a combination of frameworks and libraries that have been added over time. It uses python templates (.mako files), Knockout.js, jQuery, Bootstrap, plain javascript, Vue and React.js. The Hue team is planning on migrating all existing frontend code to React.js. This section explains how to contribute to Hue using React.js.

## Adding new components to Hue
If you want to add a new component as a descendant to an already existing react component it can be imported and used as normal. Components that are globally reused throughout Hue should be created in the folder [reactComponents](https://github.com/cloudera/hue/tree/master/desktop/core/src/desktop/js/reactComponents) and application specific components should be created in the component folder (or subfolder) of that app, e.g. a component specific to the Editor's result section should be created in [apps/editor/components/result](https://github.com/cloudera/hue/tree/master/desktop/core/src/desktop/js/apps/editor/components/result)

If you want to add a react component where there currently is no react ancestor in the DOM you will have to integrate it as a react root node in the page itself, either directly in an HTML page or by using the Knockout-to-React bridge. There is currently no Vue-to-React bridge in Hue. 

### HTML/Mako page integration
If your react component isn't dependent on any Knockout observables or Vue components you can integrate it by adding a small script and a component reference directly in the HTML code. The following example integrates MyComponent as a react root in an HTML/mako file.

 ```HTML
 <script type="text/javascript">
   (function () {
     window.createReactComponents('#some-container');
   })();
 </script>
 
 <div id="some-container">
   <MyComponent data-reactcomponent='MyComponent' data-props='{"myObj": {"id": 1}, "children": "mako template only", "version" : "${sys.version_info[0]}"}'></MyComponent>
 </div>
 ```

The MyComponent tag must be present as a descendant of the DOM element specified by the selector (#some-container) when this script runs. The attribute `data-reactcomponent` is mapped to the component name and `data-props` contains the props in JSON format.

 The component must also be imported and added to the file [js/reactComponents/imports.js](https://github.com/cloudera/hue/blob/master/desktop/core/src/desktop/js/reactComponents/imports.js) 

 ```js
  case 'MyComponent':
    return (await import('./MyComponent/MyComponent')).default;  
 ```
 
 ### Knockout.js integration
 If the new component is dependent on one or more Knockout observables you should use the Knockout-to-React bridge provided by the KO-binding `reactWrapper`. The binding expects the name of the react component and the react props (i.e. the KO observables of interest) as shown in the example below. 

 ```HTML
 <MyComponent data-bind="reactWrapper: 'MyComponent', props: { executable: activeExecutable }"></MyComponent> 
 ```

 ## Writing React components
 Hue react components are written as functional components in [Typescript](https://www.typescriptlang.org/) with styles written in external [SCSS](https://sass-lang.com/) files using [BEM notation](https://getbem.com/). The component tsx file needs to import the scss file. Each component should normally be placed in a folder with the same name as the component itself. Test files, mocks and styles are placed in the same folder. Mock files are optional.

```
components/MyComponent
│   MyComponent.tsx
│   MyComponent.scss    
│   MyComponent.test.tsx
│
└── Mocks
│   │   MyComponent.tsx
``` 
 
Hue does not use the React PropTypes or defaulProps. Instead type checking for the component props is done using an interface and default values are set using ES6 default parameters.

### i18n
All texts exposed to the end user (paragraphs, labels, alt texts, aria text etc) should be internationalized. To help with this Hue has a hook called `useTranslation` in module [i18nReact](https://github.com/cloudera/hue/blob/master/desktop/core/src/desktop/js/utils/i18nReact.ts). This is a wrapper around the hook provided by the external package `react-i18next`.

```js
const { t } = i18nReact.useTranslation();
const myGreeting = t('Hello');
```

The useTranslation hook will automatically suspend your component from rendering until the language files have been loaded from the backend. If you want to provide your own loading indicator you can disable the suspense with the config object as shown below. The `ready` property will be false until the translate function is ready to use. Unless you are writing a React root component this is normally not something you have to think about.

```js
const { t, ready } = i18nReact.useTranslation(undefined, { useSuspense: false });`
```

The useTranslation hook is automatically mocked in the unit tests. The json based language files used by i18nReact are located in folder [src/desktop/static/desktop/locales](https://github.com/cloudera/hue/blob/master/desktop/core/src/desktop/static/desktop/locales/) and the default namespace is `translation`. See [i18next](https://github.com/i18next/i18next) for more info.



### Application wide communication
For communication with non react based parts of Hue there is a publish–subscribe messaging system called [huePubsub](https://github.com/cloudera/hue/blob/master/desktop/core/src/desktop/js/utils/huePubSub.ts). To publish a message, call the `publish` function with a topic. You can subscribe to a topic using the hook [usePubSub](https://github.com/cloudera/hue/blob/master/desktop/core/src/desktop/js/reactComponents/useHuePubSub.ts) which will force your functional component to rerender once a message matching the topic is published. In the example below the editCursor state is updated by useHuePubSub each time a CURSOR_POSITION_CHANGED_EVENT is published.

```js
const editorCursor = useHuePubSub<EditorCursor>({ topic: CURSOR_POSITION_CHANGED_EVENT });
```


 ## Unit testing
 Tests are written using [Jest](https://jestjs.io/) and [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/). New test files will be automatically picked up by the test runner which is started with the command `npm run test`. Try to use the `userEvent` instead of the low level `fireEvent` when simulating user events. Below is a simple test file example.

 ```js
import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';

import MyComponent from './MyComponent';

describe('MyComponent', () => {  

  test('disables after click', async () => {
    // It is recommended to call userEvent.setup per test
    const user = userEvent.setup();
    render(<MyComponent />);
    // Insctruct the "user" to click the button with the text "Click me"
    const btn = screen.getByRole('button', { name: 'Click me' });
    expect(btn).not.toBeDisabled();
    await user.click(btn);
    
    expect(btn).toBeDisabled();
  });
});
 ```