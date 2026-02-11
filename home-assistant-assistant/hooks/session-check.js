#!/usr/bin/env node
// Session start environment check for the home-assistant-assistant plugin.
// Outputs JSON with additionalContext for async hook delivery.

const fs = require('fs');
const e = process.env;

const warnings = [];
const status = [];

// 1. Git repo check
try {
  require('child_process').execSync('git rev-parse --is-inside-work-tree', { stdio: 'pipe' });
} catch {
  warnings.push('Current directory is not a git repository. The deploy workflow requires git.');
}

// 2. configuration.yaml check
if (!fs.existsSync('configuration.yaml')) {
  warnings.push('No configuration.yaml found. This may not be a Home Assistant config directory. Commands like /ha-deploy and /ha-validate expect to run from the HA config root.');
}

// 3. HASS_TOKEN check (never print the value)
if (!e.HASS_TOKEN) {
  warnings.push('HASS_TOKEN is not set. hass-cli commands will fail.');
} else {
  status.push(`HASS_TOKEN: set (${e.HASS_TOKEN.length} chars)`);
}

// 4. HASS_SERVER check
if (!e.HASS_SERVER) {
  warnings.push('HASS_SERVER is not set. hass-cli commands will fail.');
} else {
  status.push(`HASS_SERVER: ${e.HASS_SERVER}`);
}

// 5. Onboarding check
const settingsFile = '.claude/settings.local.json';
if (fs.existsSync(settingsFile)) {
  status.push('Settings file: found');
  try {
    const settings = JSON.parse(fs.readFileSync(settingsFile, 'utf8'));
    if (!settings.deploy || !settings.deploy.pull_method) {
      warnings.push('Deploy pull method not configured. Run /ha-onboard to set it up, or /ha-deploy will ask on first use.');
    }
  } catch { /* ignore parse errors */ }
} else {
  warnings.push('No settings file found. If this is your first time, run /ha-onboard to get started.');
}

// Build context message
let context = '=== Home Assistant Assistant: Session Diagnostics ===\n';
if (status.length > 0) {
  context += status.join('\n') + '\n';
}
if (warnings.length > 0) {
  context += '\nWarnings:\n';
  warnings.forEach(w => { context += `  - ${w}\n`; });
  const missingEnv = warnings.some(w => w.includes('HASS_TOKEN') || w.includes('HASS_SERVER'));
  const missingConfig = warnings.some(w => w.includes('configuration.yaml'));
  if (missingEnv) {
    context += '\nACTION REQUIRED: Setup is incomplete. Before handling the user\'s request, you MUST invoke the /ha-onboard skill to walk them through setup. Acknowledge the user\'s request, explain that setup needs to be completed first, then launch /ha-onboard.';
  } else if (missingConfig) {
    context += '\nACTION REQUIRED: You are NOT in a Home Assistant config directory (no configuration.yaml found). Before handling the user\'s request, you MUST invoke the /ha-onboard skill. It will determine whether the user already has their config checked out locally or needs to set up git from scratch.';
  } else {
    context += '\nNote: Some non-critical warnings above. Briefly mention them to the user, then proceed with their request normally.';
  }
} else {
  context += '\nAll checks passed. Environment is ready.';
}

// Skill routing guide — helps the model pick the right plugin skill
context += '\n\nPlugin skill routing:';
context += '\n  - Entity renaming/naming conventions → /ha-naming';
context += '\n  - Execute a naming plan → /ha-apply-naming';
context += '\n  - Deploy config changes → /ha-deploy';
context += '\n  - Validate config → /ha-validate';
context += '\n  - Analyze/improve setup → /ha-analyze';
context += '\n  - New device setup → /ha-devices';
context += '\n  - Create automations/scripts/scenes → /ha-automations, /ha-scripts, /ha-scenes';

context += '\n=====================================================';

// Output JSON for async hook delivery
console.log(JSON.stringify({
  hookSpecificOutput: {
    hookEventName: 'SessionStart',
    additionalContext: context
  }
}));
