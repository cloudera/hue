import huePubSub from 'utils/huePubSub';
import { koSetup } from 'jest/koTestUtils';
import { NAME } from './ko.executableActions';
import { EXECUTABLE_UPDATED_EVENT, EXECUTION_STATUS } from 'apps/notebook2/execution/executable';
import { sleep } from 'utils/hueUtils';

describe('ko.executableActions.js', () => {
  const setup = koSetup();

  it('should render component', async () => {
    const mockExecutable = {
      cancel: () => {},
      cancelBatchChain: () => {},
      execute: () => {},
      isPartOfRunningExecution: () => false,
      isReady: () => true,
      reset: () => {},
      nextExecutable: {},
      status: EXECUTION_STATUS.ready
    };
    const activeExecutable = () => mockExecutable;
    activeExecutable.prototype.subscribe = () => {};
    const element = await setup.renderComponent(NAME, {
      activeExecutable: activeExecutable
    });

    expect(element.querySelector('[data-test="' + NAME + '"]')).toBeTruthy();
  });

  it('should handle execute and stop clicks', async () => {
    let executeCalled = false;
    let cancelCalled = false;
    const mockExecutable = {
      cancel: () => {
        cancelCalled = true;
      },
      cancelBatchChain: () => {
        cancelCalled = true;
      },
      execute: async () => {
        executeCalled = true;
      },
      isPartOfRunningExecution: () => false,
      isReady: () => true,
      reset: () => {},
      nextExecutable: {},
      status: EXECUTION_STATUS.ready
    };
    const activeExecutable = () => mockExecutable;
    activeExecutable.prototype.subscribe = () => {};
    const wrapper = await setup.renderComponent(NAME, {
      activeExecutable: activeExecutable
    });

    // Click play
    expect(executeCalled).toBeFalsy();
    expect(wrapper.querySelector('[data-test="execute"]')).toBeTruthy();
    expect(wrapper.querySelector('[data-test="stop"]')).toBeFalsy();
    wrapper.querySelector('[data-test="execute"]').click();

    await sleep(0);

    expect(executeCalled).toBeTruthy();
    mockExecutable.status = EXECUTION_STATUS.running;
    huePubSub.publish(EXECUTABLE_UPDATED_EVENT, mockExecutable);

    await setup.waitForKoUpdate();

    // Click stop
    expect(cancelCalled).toBeFalsy();
    expect(wrapper.querySelector('[data-test="execute"]')).toBeFalsy();
    expect(wrapper.querySelector('[data-test="stop"]')).toBeTruthy();
    wrapper.querySelector('[data-test="stop"]').click();

    expect(cancelCalled).toBeTruthy();
  });
});
