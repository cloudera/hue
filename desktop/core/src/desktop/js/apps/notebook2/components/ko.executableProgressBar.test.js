import huePubSub from 'utils/huePubSub';
import { koSetup } from 'jest/koTestUtils';
import { NAME } from './ko.executableProgressBar';
import { EXECUTABLE_UPDATED_EVENT, EXECUTION_STATUS } from 'apps/notebook2/execution/executable';

describe('ko.executableProgressBar.js', () => {
  const setup = koSetup();

  it('should render component', async () => {
    const mockExecutable = {
      status: EXECUTION_STATUS.ready,
      progress: 0
    };
    const activeExecutable = () => mockExecutable;
    activeExecutable.prototype.subscribe = () => {};
    const element = await setup.renderComponent(NAME, {
      activeExecutable: activeExecutable
    });

    expect(element.querySelector('[data-test="' + NAME + '"]')).toBeTruthy();
  });

  it('should reflect progress updates', async () => {
    const mockExecutable = {
      status: EXECUTION_STATUS.ready,
      progress: 0
    };
    const activeExecutable = () => mockExecutable;
    activeExecutable.prototype.subscribe = () => {};

    const wrapper = await setup.renderComponent(NAME, {
      activeExecutable: activeExecutable
    });

    // Progress should be 2% initially
    expect(wrapper.querySelector('[data-test="bar"]').style['width']).toEqual('2%');

    mockExecutable.status = EXECUTION_STATUS.running;
    mockExecutable.progress = 10;
    huePubSub.publish(EXECUTABLE_UPDATED_EVENT, mockExecutable);
    await setup.waitForKoUpdate();

    expect(wrapper.querySelector('[data-test="bar"]').style['width']).toEqual('10%');
  });

  it('should be 100% and have .progress-danger when failed', async () => {
    const mockExecutable = {
      status: EXECUTION_STATUS.ready,
      progress: 0
    };
    const activeExecutable = () => mockExecutable;
    activeExecutable.prototype.subscribe = () => {};
    const wrapper = await setup.renderComponent(NAME, {
      activeExecutable: activeExecutable
    });

    expect(wrapper.querySelector('[data-test="bar"]').style['width']).toEqual('2%');
    expect(wrapper.querySelector('[data-test="' + NAME + '"].progress-danger')).toBeFalsy();

    mockExecutable.status = EXECUTION_STATUS.failed;
    mockExecutable.progress = 10;
    huePubSub.publish(EXECUTABLE_UPDATED_EVENT, mockExecutable);
    await setup.waitForKoUpdate();

    expect(wrapper.querySelector('[data-test="bar"]').style['width']).toEqual('100%');
    expect(wrapper.querySelector('[data-test="' + NAME + '"].progress-danger')).toBeTruthy();
  });
});
