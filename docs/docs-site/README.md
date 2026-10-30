# Docs site

The source of [docs.gethue.com](https://docs.gethue.com), built with [Hugo](https://gohugo.io).

## Update the GetHue version

The docs depend on the `gethue` npm package for the live demos. Follow these steps to update it.

### Prerequisites

- Node.js 22.13 or later
- A shell in the `docs/docs-site` directory

### 1. Install GetHue

Replace `x.x.x` with the version you want to use:

```bash
npm install --save-dev gethue@x.x.x
```

### 2. Update the static resources

```bash
npm run update-static
```

`git status` shows changes in `package.json`, `package-lock.json`, and `static/js/gethue/`.

Run `hugo serve` and check that the docs UI uses the updated resources.

### 3. Commit the changes

To share the new version, commit the changed files.
