# Intent Classifier Module

Classifies user intent for time-based automations to prevent incorrect pattern substitution.

> **Safety Invariant #2:** No semantic substitutions unless equivalence conditions are satisfied.
> See `references/safety-invariants.md` for full details.

## Purpose

Users describe time-based behavior in natural language. The same phrase can mean different things:

- "Turn off after 5 minutes" - After what? Motion stops? Light turns on?
- "Wait 5 minutes" - Pure delay, or conditional on something remaining true?

This module classifies intent to select the correct automation pattern.

## The Two Patterns

### Pattern A: Inactivity Detection

**User intent:** "Do X after Y has been inactive for duration Z"

**Characteristics:**
- Action should ONLY happen if condition remains true for the entire duration
- If condition becomes false during wait, timer should RESET
- Common triggers: motion sensors, door sensors, presence

**Correct implementation:**
```yaml
triggers:
  - trigger: state
    entity_id: binary_sensor.motion
    to: "off"
    for: "00:05:00"  # Built-in "still off" check
actions:
  - action: light.turn_off
```

**Why timers fail here:**
```yaml
# WRONG - timer doesn't cancel if motion resumes!
triggers:
  - trigger: state
    entity_id: binary_sensor.motion
    to: "off"
actions:
  - action: timer.start
    data:
      duration: "00:05:00"
# If motion detected during timer, lights still turn off!
```

### Pattern B: Pure Delay

**User intent:** "Wait duration X, then do Y"

**Characteristics:**
- Action should happen after fixed time regardless of state changes
- No cancellation condition
- Common uses: notifications, scheduled tasks, sequences

**Correct implementation:**
```yaml
actions:
  - delay: "00:05:00"
  - action: notify.mobile_app
    data:
      message: "Reminder!"
```

Or with timer helper (for visibility/cancellation):
```yaml
actions:
  - action: timer.start
    target:
      entity_id: timer.reminder
    data:
      duration: "00:05:00"
```

## Classification Rules

### Keyword Analysis

| Keywords | Classification | Confidence |
|----------|---------------|------------|
| "no motion", "no movement", "inactive" | Inactivity | High |
| "stops", "becomes idle", "goes quiet" | Inactivity | High |
| "after [sensor] is off for" | Inactivity | High |
| "wait", "delay", "pause" | Pure Delay | High |
| "in X minutes", "after X minutes" | Ambiguous | Low |
| "timeout", "expires" | Ambiguous | Medium |

### Context Analysis

When keywords are ambiguous, check the trigger:

| Trigger Type | Likely Intent |
|--------------|---------------|
| Motion sensor → off | Inactivity |
| Door sensor → closed | Inactivity |
| Presence → not_home | Inactivity |
| Time-based | Pure Delay |
| Manual trigger | Pure Delay |
| Button press | Pure Delay |

### Disambiguation Questions

When confidence is low, ask:

```markdown
I want to make sure I understand the timing correctly:

**Option A - Inactivity:** Turn off lights only if motion stays inactive
for the full 5 minutes. If motion is detected during that time, the
timer resets.

**Option B - Fixed delay:** Turn off lights exactly 5 minutes after
motion stops, regardless of what happens during that time.

Which behavior do you want?
```

## Output Contract

Classification must return:

```markdown
## Intent Classification

**Input:** "Turn off kitchen lights 5 minutes after no motion"

**Classification:** Inactivity Detection
**Confidence:** High
**Reasoning:**
- "no motion" keyword indicates inactivity pattern
- Trigger is motion sensor going to "off"
- User expects lights to stay on if motion resumes

**Recommended Pattern:**
```yaml
triggers:
  - trigger: state
    entity_id: binary_sensor.kitchen_motion
    to: "off"
    for: "00:05:00"
```

**Timer Alternative:** Only valid if cancel-on-motion logic is added
```

## Timer Substitution Rules

Timers are ONLY acceptable for inactivity if ALL of these are true:

1. Timer starts when sensor goes to inactive state
2. Timer cancels/resets if sensor returns to active state
3. Action re-checks sensor state at timer expiry
4. User explicitly requested timer-based approach

**Valid timer-based inactivity:**
```yaml
# Automation 1: Start timer on motion off
triggers:
  - trigger: state
    entity_id: binary_sensor.motion
    to: "off"
actions:
  - action: timer.start
    target:
      entity_id: timer.motion_delay
    data:
      duration: "00:05:00"

# Automation 2: Cancel timer on motion on
triggers:
  - trigger: state
    entity_id: binary_sensor.motion
    to: "on"
actions:
  - action: timer.cancel
    target:
      entity_id: timer.motion_delay

# Automation 3: Turn off on timer finish (with re-check)
triggers:
  - trigger: event
    event_type: timer.finished
    event_data:
      entity_id: timer.motion_delay
conditions:
  - condition: state
    entity_id: binary_sensor.motion
    state: "off"
actions:
  - action: light.turn_off
```

**This requires 3 automations vs 1 with `for:` - always prefer `for:` unless user has specific timer needs.**

## Integration Points

- **ha-automations skill**: Must classify before generating
- **ha-conventions skill**: Timer preference should not override classification
- **ha-troubleshooting skill**: Check if timer misuse caused the bug
