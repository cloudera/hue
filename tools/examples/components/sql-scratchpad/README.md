# Getting Started with SQL Scratchpad

This projects demonstrates how you can use the Hue web components from within a React project to
create a SQL Scratchpad.

It's based on a clean create-react-app project, relevant changes are:

- gethue dependency in package.json, note that this can also be pulled in from the npm repo by specifing a version > 4.9)
- "components" folder with React wrappers around the Hue web components
- App.tsx using the React wrappers

We wrap the web components to be able to set certain attributes/properties on the web component elements that are required by the web components.

## To run this project

1. Setup Hue to allow CORS, in your hue .ini add:
```
  [desktop]
    cors_enabled=true
```
2. Make sure Hue has a "hue" user with the password "hue" (this will be improved soon)
3. Go to the Hue root folder `cd ../../../../`
4. `npm install`
5. `npm run webpack-npm`
6. Go to the example project `cd tools/examples/components/sql-scratchpad`
7. `npm install`
8. `npm start`
9. Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

## Base project creation steps (for reference)

1. `npx create-react-app sql-scratchpad --template typescript`
2. add `"gethue": "file:../../../../npm_dist"` to dependencies in package.json
3. add `SKIP_PREFLIGHT_CHECK=true` to .env (required when running inside nested Hue folder)