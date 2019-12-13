import { koSetup } from 'jest/koTestUtils';
import { NAME } from './ko.savedQueries';

describe('ko.savedQueries.js', () => {
  const setup = koSetup();

  it('should render component', async () => {
    const element = await setup.renderComponent(NAME, {
      currentTab: () => undefined
    });

    expect(element.innerHTML).toMatchSnapshot();
  });
});
