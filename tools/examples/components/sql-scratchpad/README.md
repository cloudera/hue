# Getting Started with SQL Scratchpad

This projects demonstrates how you can use the Hue web components from within a React project to
create a SQL Scratchpad.

It's based on a clean create-react-app project, relevant changes are:

- gethue dependency in package.json, tested with version 4.9.3
- "components" folder with React wrappers around the Hue web components
- App.tsx using the React wrappers

We wrap the web components to be able to set certain attributes/properties on the web component elements that are required by the web components.

## To run this project

1. Setup Hue to allow CORS, in your hue .ini add:
```
  [desktop]
    cors_enabled=true
```
2. Go to the example project `cd tools/examples/components/sql-scratchpad`
3. `npm install`
4. `npm start`
5. Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

To kill it press `ctrl-c` in the terminal

## To use this project while developing the Hue NPM package,

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
2. add `"gethue": "file:../../../../npm_dist"` to dependencies in package.json
3. add `SKIP_PREFLIGHT_CHECK=true` to .env (required when running inside nested Hue folder)
