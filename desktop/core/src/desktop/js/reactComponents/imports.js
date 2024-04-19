// ADD NEW RACT COMPONENTS HERE
// We need a way to match an imported module with a component name
// so we handle the imports dynamically for that reason.
export async function loadComponent(name) {
  switch (name) {
    // Page specific components here
    case 'ReactExample':
      return (await import('../apps/editor/components/result/reactExample/ReactExample')).default;

    case 'StorageBrowserPage':
      return (await import('../apps/storageBrowser/StorageBrowserPage/StorageBrowserPage')).default;

    // Application global components here
    case 'AppBanner':
      return (await import('./AppBanner/AppBanner')).default;

    case 'AlertComponent':
      return (await import('./AlertComponent/AlertComponent')).default;

    case 'ReactExampleGlobal':
      return (await import('./ReactExampleGlobal/ReactExampleGlobal')).default;

    case 'FileChooserWithButton':
      return (await import('./FileChooser/FileChooserWithButton/FileChooserWithButton')).default;

    case 'WelcomeTour':
      return (await import('./WelcomeTour/WelcomeTour')).default;

    case 'TaskBrowser':
      return (await import('./TaskBrowser/TaskBrowser')).default;

    default:
      console.error(`A placeholder component is rendered because you probably forgot to include your new component in the 
      loadComponent function of reactComponents/imports.js`);
      return (await import('./FallbackComponent')).default;
  }
}
