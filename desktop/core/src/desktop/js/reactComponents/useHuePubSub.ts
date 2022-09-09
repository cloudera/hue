import { useState, useEffect } from 'react';
import huePubSub from '../utils/huePubSub';

// Basic helper hook to let a component subscribe to a huePubSub topic and rerender for each message
// by placing the message/info in a state that is automatically updated.
// Use with caution and preferrably only at the top level component in your component tree since
// we don't want to have states stored all over the app.

export function useHuePubSub<Type>({
  topic,
  app
}: {
  topic: string;
  app?: string;
}): Type | undefined {
  const [huePubSubState, setHuePubSubState] = useState({ info: undefined });

  useEffect(() => {
    const pubSub = huePubSub.subscribe(
      topic,
      info => {
        // Always create a new state so that the react component is rerendered even
        // if the info is the same as previous info. This is to stay aligned with the idea
        // of having a component being notified for EVERY message for the topics it subscribes to.
        setHuePubSubState(() => ({ info }));
      },
      app
    );

    return () => {
      // Remove huePubSub subscription
      pubSub.remove();
    };
  });

  return huePubSubState.info;
}
