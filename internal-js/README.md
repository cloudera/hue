### UI Tests

To run Jest tests for the internal-js (only), in the Hue root folder:

    npm run test -- -c="internal-js/jest.config.js"

Or, to have Jest continuously watch for changes:

    npm run test-dev -- -c="internal-js/jest.config.js"

### Linting

To run the linter, in the Hue root folder:

    npm run env -- eslint internal-js/apps

Or, to have the linter automatically fix what it can:

    npm run env -- eslint internal-js/apps --fix
