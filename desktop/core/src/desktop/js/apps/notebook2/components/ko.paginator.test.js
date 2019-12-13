import { koSetup } from 'jest/koTestUtils';
import { NAME } from './ko.paginator';

describe('ko.paginator.js', () => {
  const setup = koSetup();

  it('should render component', async () => {
    const element = await setup.renderComponent(NAME, {
      totalPages: () => 5,
      currentPage: () => 1
    });

    expect(element.innerHTML).toMatchSnapshot();
  });
});
