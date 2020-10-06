module.exports = {
  moduleFileExtensions: ['js', 'jsx', 'ts', 'tsx', 'json', 'vue'],
  transform: {
    "^.+\\.(js|ts)$": "babel-jest",
    "^.+\\.vue$": "vue-jest"
  },
  "moduleNameMapper": {
    "\\.(css|less|scss|sass)$": "identity-obj-proxy"
  },
  moduleDirectories: ['node_modules', '<rootDir>../desktop/core/src/desktop/js'],
  modulePaths: ['<rootDir>../desktop/core/src/desktop/js'],
  testMatch: ['<rootDir>/../internal-js/apps/**/*.test.(js|jsx|ts|tsx)'],
  testEnvironment: 'jest-environment-jsdom-sixteen',
  testURL: 'https://www.gethue.com/hue',
  setupFilesAfterEnv: ['<rootDir>/../desktop/core/src/desktop/js/jest/jest.init.js']
};
