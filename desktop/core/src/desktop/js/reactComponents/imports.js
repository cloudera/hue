// ADD NEW REACT COMPONENTS HERE
// We need a way to match an imported module with a component name
// so we handle the imports dynamically for that reason.
export async function loadComponent(name) {
  switch (name) {
    // Page specific components here
    case 'ReactExample':
      return (await import('../apps/editor/components/result/reactExample/ReactExample')).default;

    case 'StorageBrowserPage':
      return (await import('../apps/storageBrowser/StorageBrowserPage')).default;

    case 'Overview':
      return (await import('../apps/admin/Overview/OverviewTab')).default;

    case 'Metrics':
      return (await import('../apps/admin/Metrics/MetricsTab')).default;

    case 'Configuration':
      return (await import('../apps/admin/Configuration/ConfigurationTab')).default;

    case 'ServerLogs':
      return (await import('../apps/admin/ServerLogs/ServerLogsTab')).default;

    // Application global components here
    case 'AppBanner':
      return (await import('./AppBanner/AppBanner')).default;

    case 'GlobalAlert':
      return (await import('./GlobalAlert/GlobalAlert')).default;

    case 'ReactExampleGlobal':
      return (await import('./ReactExampleGlobal/ReactExampleGlobal')).default;

    case 'WelcomeTour':
      return (await import('./WelcomeTour/WelcomeTour')).default;

    case 'TaskServer':
      return (await import('./TaskServer/TaskServer')).default;

    case 'FileUploadQueue':
      return (await import('./FileUploadQueue/FileUploadQueue')).default;

    default:
      console.error(`A placeholder component is rendered because you probably forgot to include your new component in the 
      loadComponent function of reactComponents/imports.js`);
      return (await import('./FallbackComponent')).default;
  }
}
