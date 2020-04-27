import { koSetup } from 'jest/koTestUtils';
import { NAME } from './ko.queryHistory';

describe('ko.queryHistory.js', () => {
  const setup = koSetup();

  it('should render component', async () => {
    const element = await setup.renderComponent(NAME, {});

    expect(element.innerHTML).toMatchSnapshot();
  });
});
