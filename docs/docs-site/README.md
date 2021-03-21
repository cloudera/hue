# Docs Site

## Update GetHue version

Docs uses GetHue for live demos. Kindly follow these steps to update GetHue to the version of your choice.

### 1. Install GetHue

    # x.x.x - Version you are updating to
    npm install --dev-save gethue@x.x.x

### 2. Update static resources

    npm run update-static

This must update the resources used in the docs. On `git status` you must see modifications on `./package.json`, `./package-lock.json` & `static/js/gethue/`. And on `hugo serve` you must see the updated resources in the docs UI.

### 3. Commit changes

If you want to share the updated version with everyone, commit the changed files.
