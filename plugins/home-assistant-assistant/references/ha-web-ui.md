# Home Assistant Web UI — Browser Automation Guidance

## Shadow DOM Architecture

Home Assistant's frontend is built with Lit/Polymer web components that use **deep Shadow DOM nesting**. A typical page element is nested 5–8 shadow roots deep:

```
<home-assistant>
  #shadow-root
    <home-assistant-main>
      #shadow-root
        <ha-panel-config>
          #shadow-root
            <ha-config-devices-dashboard>
              #shadow-root
                ...actual content...
```

## What Fails

Standard browser automation tools **will not work** with HA's UI:

- `read_page` / `get_page_text` — returns only the outermost shell, not nested shadow content
- `find` / CSS selectors — cannot pierce shadow boundaries
- `click` by text — target elements are inside shadow roots, invisible to the selector engine
- Playwright `snapshot` / standard selectors — same shadow DOM limitation

## Preferred Alternatives

**In order of preference:**

1. **hass-cli** — covers most read/write operations (state, entity, device, area, service calls)
2. **HA REST API** — `hass-cli raw get/post /api/...` for anything hass-cli doesn't wrap
3. **Python helpers** — for complex operations (registry cross-referencing, traces)
4. **Guide the user** — tell them exactly where to click in the UI (with nav path)

## When Browser Automation Is Truly Needed

If no API alternative exists (e.g., Z-Wave JS UI, add-on dashboards):

1. **Use JavaScript injection** to traverse shadow roots:
   ```javascript
   // Example: reach into Z-Wave JS UI
   document.querySelector('home-assistant')
     .shadowRoot.querySelector('home-assistant-main')
     .shadowRoot.querySelector('ha-panel-iframe')
     // ...continue traversing
   ```
2. Expect this to be **fragile** — shadow DOM structure changes between HA versions
3. **Warn the user** that browser automation with HA is unreliable before attempting it

## Do NOT

- Spend more than 2–3 attempts if browser tools return empty/incorrect results
- Install browser automation packages (Selenium, Playwright) without asking the user
- Retry the same failing selector — switch to an API-based approach instead
