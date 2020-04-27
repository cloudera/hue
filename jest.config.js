module.exports = {
  moduleFileExtensions: ['js', 'jsx'],
  moduleDirectories: ['node_modules', 'desktop/core/src/desktop/js'],
  modulePaths: ['desktop/core/src/desktop/js'],
  testMatch: ['<rootDir>/desktop/core/src/desktop/js/**/*.test.(js|jsx|ts|tsx)'],
  testEnvironment: 'jest-environment-jsdom-fourteen',
  testURL: 'https://www.gethue.com/hue',
  setupFilesAfterEnv: ['<rootDir>/desktop/core/src/desktop/js/jest/jest.init.js'],
  watchPathIgnorePatterns: ['<rootDir>/desktop/core/src/desktop/static'],
  testPathIgnorePatterns: [
    '<rootDir>/desktop/core/src/desktop/js/parse/sql/ksql/test',
    '<rootDir>/desktop/core/src/desktop/js/parse/sql/elasticsearch/test',
    '<rootDir>/desktop/core/src/desktop/js/parse/sql/phoenix/test',
    '<rootDir>/desktop/core/src/desktop/js/parse/sql/druid/test',
    '<rootDir>/desktop/core/src/desktop/js/parse/sql/presto/test',
    '<rootDir>/desktop/core/src/desktop/js/parse/sql/calcite/test',
    '<rootDir>/desktop/core/src/desktop/js/parse/sql/flink/test',
  ],
  collectCoverageFrom: ['<rootDir>/desktop/core/src/desktop/js/**/*.{js,jsx}']
};
