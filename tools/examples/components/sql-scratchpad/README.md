# Getting Started with SQL Scratchpad

This app demonstrates how to import the Hue web components from within a React project to
create a SQL Scratchpad.

It's based on a clean create-react-app project, relevant changes are:

- gethue dependency in package.json, tested with version 4.9.3
- "components" folder with React wrappers around the Hue web components
- App.tsx using the React wrappers

The components are wrapped to set certain attributes/properties on elements that are required by the web components.

There are two ways to import the SQL Scratchpad:

- from the Hue package https://www.npmjs.com/package/gethue
- from your local Hue repository (when developing above package)


## Use the published package

1. Go to the example project `cd tools/examples/components/sql-scratchpad`
2. `npm install`
3. `npm start`
4. Open [http://localhost:3000](http://localhost:3000) to view it in the browser.


## Use your local package

1. In the SQL Scratchpad project change the "gethue" dependency in `package.json` to
   ```
   "gethue": "file:../../../../npm_dist",
   ```
2. Go to the Hue root folder `cd ../../../../`
4. `npm install`
5. `npm run dev-webpack-npm`
6. Go to the example project `cd tools/examples/components/sql-scratchpad`
7. `npm install`
8. `npm start`

It will monitor changes of the related Hue sources and update npm_dist when needed, if the
SQL Scratchpad project doesn't pick up the changes a restart of the app might be needed.


## Base project creation steps (for reference)

1. `npx create-react-app sql-scratchpad --template typescript`
2. Add `"gethue": "file:../../../../npm_dist"` to dependencies in package.json
3. Add `SKIP_PREFLIGHT_CHECK=true` to .env (required when using local Hue package)
