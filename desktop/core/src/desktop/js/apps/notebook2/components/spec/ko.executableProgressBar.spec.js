import huePubSub from 'utils/huePubSub';
import { koSetup } from 'spec/jasmineSetup';
import { NAME } from '../ko.executableProgressBar';
import { EXECUTION_STATUS } from 'apps/notebook2/execution/executable';
import { EXECUTOR_UPDATED_EVENT } from 'apps/notebook2/execution/executor';

describe('ko.executableProgressBar.js', () => {
  const setup = koSetup();

  it('should render component', async () => {
    const element = await setup.renderComponent(NAME, {});

    expect(element.querySelector('[data-test="' + NAME + '"]')).toBeTruthy();
  });

  it('should reflect progress updates', async () => {
    const mockExecutor = {};
    const snippet = {
      executor: mockExecutor
    };
    const wrapper = await setup.renderComponent(NAME, {
      snippet: snippet
    });

    // Progress should be 2% initially
    expect(wrapper.querySelector('[data-test="bar"]').style['width']).toEqual('2%');

    huePubSub.publish(EXECUTOR_UPDATED_EVENT, {
      executor: mockExecutor,
      executable: {
        status: EXECUTION_STATUS.running,
        progress: 10
      }
    });
    await setup.waitForKoUpdate();

    expect(wrapper.querySelector('[data-test="bar"]').style['width']).toEqual('10%');
  });

  it('should be 100% and have .progress-danger when failed', async () => {
    const mockExecutor = {};
    const snippet = {
      executor: mockExecutor
    };
    const wrapper = await setup.renderComponent(NAME, {
      snippet: snippet
    });

    expect(wrapper.querySelector('[data-test="bar"]').style['width']).toEqual('2%');
    expect(wrapper.querySelector('[data-test="' + NAME + '"].progress-danger')).toBeFalsy();

    huePubSub.publish(EXECUTOR_UPDATED_EVENT, {
      executor: mockExecutor,
      executable: {
        status: EXECUTION_STATUS.failed,
        progress: 10
      }
    });
    await setup.waitForKoUpdate();

    expect(wrapper.querySelector('[data-test="bar"]').style['width']).toEqual('100%');
    expect(wrapper.querySelector('[data-test="' + NAME + '"].progress-danger')).toBeTruthy();
  });
});
