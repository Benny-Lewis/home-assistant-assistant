# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Claude Code plugin for Home Assistant integration. The plugin will allow Claude Code to interact with Home Assistant instances — controlling devices, querying states, and automating tasks through natural language.

## Current State

The project is in pre-development. The `resources/anthropic/` directory contains curated reference links to official Anthropic documentation for plugins, skills, subagents, and related APIs. These serve as the canonical sources when building out the plugin.

## Key Reference Documentation

All official docs are indexed in `resources/anthropic/README.md`:
- **Plugins**: End-to-end plugin guide, component schemas, marketplace distribution
- **Skills**: Creating skills for Claude Code and the Claude API
- **Subagents**: Agent creation and orchestration patterns
- Social context from Claude Code creator tweets (unverified, user-provided)

## Plugin Architecture (Target)

This project follows the Claude Code plugin structure. Key concepts:
- `plugin.json` — Plugin manifest with metadata and component discovery
- Skills (SKILL.md files) — Invoked by the model or user via slash commands
- Agents — Subagents with specialized system prompts and tool access
- Hooks — Event-driven automation (PreToolUse, PostToolUse, etc.)
- MCP servers — External tool integration (likely used for Home Assistant API communication)

## Development Notes

- No build system, tests, or CI configured yet
- Not yet a git repository
- When scaffolding the plugin, consult `resources/anthropic/plugins/README.md` for the official plugin guide links
- Skills and slash commands are effectively the same thing (per creator tweets in `resources/anthropic/social/`)
