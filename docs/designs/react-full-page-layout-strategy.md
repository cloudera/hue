# React Full-Page Layout Strategy

## Overview

This document describes the pattern for creating React pages that fill the full browser height in Hue, ensuring consistent behavior without affecting legacy code.

## Pattern for Admin Pages (with Navbar)

Admin pages in Hue have a custom navbar (about_layout.mako menubar) and need special handling to fill the remaining height.

### Template Structure

```mako
<%namespace name="layout" file="about_layout.mako" />

${layout.menubar(section='section_name')}

<div id="component-container" class="admin-page-full-height">
  <ComponentName class='antd cuix' data-reactcomponent='ComponentName'></ComponentName>
</div>

<style type="text/css">
  .admin-page-full-height {
    position: absolute;
    top: 50px;           /* Height of the admin menubar */
    left: 0;
    right: 0;
    bottom: 0;
    overflow: hidden;
  }

  .admin-page-full-height > * {
    height: 100%;
  }
</style>

<script src="${ static('desktop/js/component-inline.js') }" type="text/javascript"></script>
```

### Inline Script

```javascript
(function () {
  window.createReactComponents('#component-container');
})();
```

### Component SCSS

```scss
@import '../../../components/styles/variables';

.my-component.antd.cuix {
  height: 100%;
  overflow-y: auto;
  background-color: $fluidx-gray-100;
  padding: 24px;

  // ... rest of component styles
}
```

### Key Points

1. **Container positioning**: Use `position: absolute` with `top`, `left`, `right`, `bottom` to fill available space
2. **Top offset**: Adjust the `top` value based on navbar height (50px for admin menubar)
3. **Component height**: Set `height: 100%` and `overflow-y: auto` on the React component wrapper
4. **Background**: The background color fills the entire height

## Pattern for Embeddable Pages (Main Hue Layout)

For pages that use the main Hue layout with `embeddable_*` divs:

### Using Existing Embeddable Containers

The main `hue.mako` layout provides embeddable containers that are already set up:

```html
<div class="page-content">
  <div id="embeddable_myapp" class="embeddable"></div>
</div>
```

The `.page-content` class has:

- `flex: 1` - takes remaining space
- `position: relative`
- `overflow-x: auto`

### React Component Pattern

For components rendered in embeddable containers, use the shared mixins:

```scss
@import 'mixins';

.my-app.antd.cuix {
  @include fillAbsolute;
  @include flexRowLayout;

  background-color: $fluidx-gray-100;

  .my-app__container {
    flex: 1;
    overflow-y: auto;
    padding: 24px;
  }
}
```

### Available Mixins

From `/desktop/core/src/desktop/js/components/styles/_mixins.scss`:

```scss
// Fill absolute positioning
@mixin fillAbsolute {
  position: absolute;
  inset: 0 0 0 0;
}

// Flex column layout with hidden overflow
@mixin flexRowLayout {
  @include display-flex();
  @include flex-direction(column);
  overflow: hidden;
}
```

## Examples in the Codebase

### Admin Pages

- **Overview**: `apps/about/src/about/templates/admin_wizard.mako`
- **Metrics**: `desktop/core/src/desktop/templates/metrics.mako`
- **Server Logs**: `desktop/core/src/desktop/templates/logs.mako`
- **Configuration**: `desktop/core/src/desktop/templates/dump_config.mako`

### Embeddable Pages

- **Importer**: `desktop/core/src/desktop/js/apps/newimporter/ImporterPage.scss`
- **Storage Browser**: Uses embeddable pattern

## Common Issues and Solutions

### Issue: Background doesn't fill to bottom

**Solution**: Ensure all parent elements have proper height:

1. Container has `position: absolute` with inset values OR `height: 100%`
2. Component has `height: 100%`
3. Background is on the element with height set

### Issue: Content not scrollable

**Solution**: Add `overflow-y: auto` to the component wrapper that has `height: 100%`

### Issue: Top content cut off

**Solution**: Adjust the `top` value in the container positioning to account for navbar/header height

## Future Improvements

Consider creating a shared SCSS utility file for common full-page patterns:

```scss
// _page-layouts.scss
.hue-full-page {
  @include fillAbsolute;
  @include flexRowLayout;
}

.hue-full-page-scrollable {
  height: 100%;
  overflow-y: auto;
}
```

## Migration Checklist

When converting an existing page to full-height:

- [ ] Update template with container div and positioning styles
- [ ] Add `height: 100%` and `overflow-y: auto` to component SCSS
- [ ] Update inline script to target correct container
- [ ] Test with different screen sizes
- [ ] Verify scrolling behavior
- [ ] Check that background fills entire page
- [ ] Ensure no impact on surrounding pages

## Best Practices

1. **Use consistent class names**: `{feature}-container` for wrappers
2. **Keep positioning styles in template**: Makes it clear how the page is laid out
3. **Use SCSS variables**: For colors, spacing, etc.
4. **Test thoroughly**: Check different viewport heights and widths
5. **Document deviations**: If you need a different pattern, document why

---

**Last Updated**: October 2025
**Maintainer**: Frontend Team

