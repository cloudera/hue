import huePubSub from 'utils/huePubSub';
import { koSetup } from 'spec/jasmineSetup';
import { NAME } from '../ko.snippetExecuteActions';
import { EXECUTION_STATUS } from 'apps/notebook2/execution/executableStatement';
import { EXECUTOR_UPDATED_EVENT } from 'apps/notebook2/execution/executor';

describe('ko.snippetExecuteActions.js', () => {
  const setup = koSetup();

  it('should render component', async () => {
    const element = await setup.renderComponent(NAME, {});

    expect(element.querySelector('[data-test="' + NAME + '"]')).toBeTruthy();
  });

  it('should handle execute and stop clicks', async () => {
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
    expect(wrapper.querySelector('[data-test="execute"]')).toBeTruthy();
    expect(wrapper.querySelector('[data-test="stop"]')).toBeFalsy();
    wrapper.querySelector('[data-test="execute"]').click();

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
    expect(wrapper.querySelector('[data-test="execute"]')).toBeFalsy();
    expect(wrapper.querySelector('[data-test="stop"]')).toBeTruthy();
    wrapper.querySelector('[data-test="stop"]').click();

    expect(cancelCalled).toBeTruthy();
  });
});
