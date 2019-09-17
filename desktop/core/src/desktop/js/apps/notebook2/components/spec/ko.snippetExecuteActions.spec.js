import huePubSub from 'utils/huePubSub';
import { koSetup } from 'spec/jasmineSetup';
import { NAME } from '../ko.snippetExecuteActions';
import { EXECUTION_STATUS } from 'apps/notebook2/execution/executableStatement';
import { EXECUTOR_UPDATED_EVENT } from 'apps/notebook2/execution/executor';

describe('ko.snippetExecuteActions.js', () => {
  const setup = koSetup();

  it('should render component', async () => {
    const element = await setup.renderComponent(NAME, {});

    expect(element.querySelector('.snippet-execute-actions')).toBeTruthy();
  });

  it('should handle play and stop clicks', async () => {
    let executeCalled = false;
    let cancelCalled = false;
    const mockExecutor = {
      cancel: () => {
        cancelCalled = true;
      }
    };
    const snippet = {
      executor: () => mockExecutor,
      execute: () => {
        executeCalled = true;
      }
    };
    const wrapper = await setup.renderComponent(NAME, {
      snippet: snippet
    });

    // Click play
    expect(executeCalled).toBeFalsy();
    expect(wrapper.querySelector('.fa-play')).toBeTruthy();
    expect(wrapper.querySelector('.fa-stop')).toBeFalsy();
    wrapper.querySelector('.fa-play').click();

    expect(executeCalled).toBeTruthy();
    huePubSub.publish(EXECUTOR_UPDATED_EVENT, {
      executor: mockExecutor,
      executable: {
        status: EXECUTION_STATUS.running
      }
    });

    await setup.waitForKoUpdate();

    // Click stop
    expect(cancelCalled).toBeFalsy();
    expect(wrapper.querySelector('.fa-play')).toBeFalsy();
    expect(wrapper.querySelector('.fa-stop')).toBeTruthy();
    wrapper.querySelector('.fa-stop').click();

    expect(cancelCalled).toBeTruthy();
  });
});
