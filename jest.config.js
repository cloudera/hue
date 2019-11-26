module.exports = {
  moduleFileExtensions: ['js', 'jsx'],
  moduleDirectories: ['node_modules', 'desktop/core/src/desktop/js'],
  modulePaths: ['desktop/core/src/desktop/js'],
  testMatch: ['<rootDir>/desktop/core/src/desktop/js/**/*.test.(js|jsx|ts|tsx)'],
  testEnvironment: 'jest-environment-jsdom-fourteen',
  testURL: 'https://www.gethue.com/hue',
  setupFilesAfterEnv: ['<rootDir>/desktop/core/src/desktop/js/jest/jest.init.js'],
  watchPathIgnorePatterns: ['<rootDir>/desktop/core/src/desktop/static']
};
