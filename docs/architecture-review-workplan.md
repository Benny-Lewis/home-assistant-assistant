# Architecture Review Workplan

Last updated: 2026-02-21
Owner: Ben + Codex

## 1. Status

Current phase: Phase 0-6 complete; review execution complete
Overall status: Complete (review phase)
Review execution status: Checkpoint 4 complete (final)
Analysis mode: Hybrid complete (incremental per document + final synthesis complete)
Document intake status: Complete (all shared sources ingested)
Cross-document synthesis status: Complete

## 2. Document Inventory

Use this table to track all source materials before analysis begins.

| ID | Title | Type | Path/Link | Owner | Priority | Read Status | Notes |
|---|---|---|---|---|---|---|---|
| DOC-001 | The Bitter Lesson (Rich Sutton) | Best Practice | `docs/architecture-review-sources/best-practices/rich-sutton-the-bitter-lesson.md` | Ben | Medium | Complete | Analyzed 2026-02-21; extracted provisional criteria on generality/scaling. |
| DOC-002 | The Complete Guide to Building Skills for Claude | Official vendor guide | `docs/architecture-review-sources/official/anthropic-complete-guide-building-skills-for-claude.md` | Ben | High | Complete | Duplicate format removed; analyzed 2026-02-21 for structure, security, testing, and operability requirements. |
| DOC-003 | Skill authoring best practices | Official vendor guide | `docs/architecture-review-sources/official/anthropic-agent-skills-best-practices.md` | Ben | High | Complete | Analyzed 2026-02-21; extracted constraints for concision, structure depth, evaluation loops, executable script patterns, and runtime/tool compatibility. |
| DOC-004 | Best Practices for Claude Code | Official vendor guide | `docs/architecture-review-sources/official/claude-code-best-practices.md` | Ben | High | Complete | Analyzed 2026-02-21; extracted constraints for verification-first delivery, context/session control, environment governance, and safe scaling patterns. |
| DOC-005 | Claude Cookbooks: Skills Introduction Notebook | Official example (Anthropic repo) | `docs/architecture-review-sources/official-examples/claude-cookbooks/anthropic-claude-cookbooks-skills-introduction.ipynb` | Ben | Medium | Complete | Analyzed 2026-02-21 with image assets captured; used as implementation-oriented evidence below canonical docs precedence. |
| DOC-006 | Claude Cookbooks: patterns/agents (tree) | Official example collection (Anthropic repo) | `docs/architecture-review-sources/official-examples/claude-cookbooks/patterns-agents/` | Ben | Medium | Complete | Analyzed 2026-02-21; includes workflow notebooks, orchestration prompts, and operational constraints for delegation/citations. |
| DOC-007 | Define success criteria and build evaluations | Official vendor guide | `docs/architecture-review-sources/official/anthropic-develop-tests.md` | Ben | High | Complete | Analyzed 2026-02-21; eval-design and grading architecture guidance. |
| DOC-008 | Demystifying evals for AI agents | Official Anthropic engineering article | `docs/architecture-review-sources/official/anthropic-demystifying-evals-for-ai-agents.html` | Ben | High | Complete | Analyzed 2026-02-21; distinct from DOC-007, focused on agent-eval systems and lifecycle operations. |
| DOC-009 | HA MCP reference implementation snapshot | External reference implementation (official project) | `docs/architecture-review-sources/reference-implementations/ha-mcp-architecture-snapshot.md` | Ben | High | Complete | Analyzed 2026-02-21 from local clone at `C:\Users\Ben\dev\ha-mcp` (`3dc098812a4dc7044c8883f57a9c2048297d3ee8`) to support Skills+MCP architecture decisions. |

Read status legend:
- Not started
- In progress
- Complete
- Blocked

## 2a. Analysis Workflow

Approved approach:
1. Analyze each document immediately after upload.
2. Extract provisional requirements, constraints, risks, and assumptions.
3. Record findings with source traceability in this workplan.
4. Keep findings provisional until all documents are uploaded.
5. Run a final cross-document synthesis pass after corpus completion.
6. Reconcile overlaps/conflicts using source precedence rules.
7. Produce the comprehensive architecture review plan only after synthesis.

Synthesis trigger phrase: "all docs uploaded" (received and satisfied on 2026-02-21)

## 2b. Per-Document Analysis Notes (Provisional)

### DOC-001 - The Bitter Lesson (Rich Sutton)

Key extracted guidance for architecture review:
- Favor general, compute-leveraging methods over brittle, hand-crafted domain heuristics in core architecture.
- Avoid embedding narrow assumptions in foundational layers when those assumptions limit scaling and future capability growth.
- Prioritize mechanisms that improve with more data, better models, or more computation.
- Keep architecture focused on meta-methods (discovery/orchestration/evaluation loops) rather than static encoded domain conclusions.

Implication for plugin review:
- We will test whether the plugin core is overfit to fixed heuristics versus designed for scalable general workflows.
- Any domain-specific logic in core paths will be flagged unless clearly justified by hard constraints.

### DOC-002 - The Complete Guide to Building Skills for Claude

Key extracted guidance for architecture review:
- Skill packaging model: `SKILL.md` is required (exact case); `scripts/`, `references/`, and `assets/` are optional but recommended for separation of concerns.
- Progressive disclosure is a core design principle: metadata for routing, main instructions for execution, linked files for detailed/reference material.
- Frontmatter is critical for activation quality: `name` in kebab-case; `description` must define both what the skill does and when it should trigger, including realistic trigger phrases.
- Security restrictions: avoid XML angle brackets in frontmatter, avoid reserved naming patterns, and keep metadata safe/static.
- Instruction quality requirements: explicit, actionable steps; clear references to bundled scripts/docs; built-in error handling and troubleshooting guidance.
- Testing guidance requires three dimensions: trigger behavior, functional correctness, and baseline-vs-skill performance comparison.
- Operability guidance includes monitoring under/over-triggering and iterating from observed failure modes.
- Context/performance guidance: keep `SKILL.md` concise, move detail to `references/`, and avoid enabling excessive numbers of skills simultaneously.
- Portability/composability: skills should work across Claude.ai, Claude Code, and API, and coexist with other skills.

Implication for plugin review:
- We will assess architecture against a strict skill-contract model: package structure, activation metadata, security-safe frontmatter, and progressive-disclosure design.
- We will verify that reliability and quality are engineered through explicit test loops and trigger telemetry, not ad hoc prompting behavior.

### DOC-003 - Skill authoring best practices

Key extracted guidance for architecture review:
- Treat context budget as a hard architectural constraint: keep instructions concise, keep `SKILL.md` under 500 lines, and rely on progressive disclosure.
- Metadata quality is foundational for discovery: `name` and `description` must satisfy strict validation and clearly express what/when in discovery-friendly wording (third-person recommended).
- Keep reference topology shallow: link reference files directly from `SKILL.md` (one level deep) to improve discoverability and reduce navigation failures.
- Use workflow-oriented instructions for complex operations: sequential checklists, explicit step boundaries, and validator-driven feedback loops.
- Use evaluation-driven development: establish baseline behavior first, create explicit evaluations, and iterate against observed failures.
- Validate across target models and real usage patterns, not only synthetic prompts.
- Prefer deterministic utility scripts for repeatable operations; scripts should handle errors directly and justify configuration constants.
- For high-risk or large batch changes, use verifiable intermediate artifacts (plan -> validate -> execute -> verify) instead of direct execution.
- Runtime constraints differ by surface (`claude.ai` vs API): package/runtime assumptions must be explicit and testable.
- MCP calls should use fully qualified tool references (`ServerName:tool_name`) to avoid routing ambiguity.
- Avoid portability anti-patterns (Windows-style paths, ambiguous path naming, excessive option branching without defaults).

Implication for plugin review:
- We will assess whether this plugin is architected as a discoverable, low-token, high-determinism system instead of a large prompt bundle.
- We will explicitly inspect for verification gates and evaluation loops before trusting high-impact automation paths.

### DOC-004 - Best Practices for Claude Code

Key extracted guidance for architecture review:
- Verification-first execution is mandatory: workflows should include tests, screenshots, or explicit output checks so the agent can self-validate.
- Use staged execution for non-trivial changes: explore -> plan -> implement -> verify/commit; skip heavyweight planning only for trivially scoped diffs.
- Prompt/input quality affects architecture outcomes: tasks should encode scope, sources, symptoms, constraints, and acceptance criteria.
- Context is the core resource constraint: architecture should support aggressive context hygiene (`/clear`, compaction, scoped investigations).
- Persistent instruction memory (`CLAUDE.md`) should stay concise and high-signal; domain-specific or occasional guidance should be moved into skills.
- Deterministic guardrails should be implemented via hooks for must-run checks, rather than relying only on advisory instructions.
- Safety boundaries should be explicit: permission allowlists/sandboxing preferred; fully unrestricted autonomy should be limited to controlled isolated environments.
- Prefer context-efficient integrations (CLI tools, MCP, skills, subagents) to reduce token-heavy manual context transfer.
- Subagents are a first-class architecture pattern for isolated research/review in separate context windows.
- Operational scale patterns (headless mode, fan-out runs, parallel sessions) require scoped tool permissions and explicit blast-radius control.
- Common failure patterns to prevent by design: "kitchen sink" sessions, repeated correction loops, overgrown instruction files, and unverified output.

Implication for plugin review:
- We will evaluate whether this plugin architecture enforces verification gates and context hygiene as built-in behavior, not optional user discipline.
- We will inspect autonomy controls and permission boundaries to ensure scalability does not increase risk beyond acceptable limits.

### DOC-005 - Claude Cookbooks: Skills Introduction Notebook

Image assets captured for analysis:
- `docs/architecture-review-sources/official-examples/claude-cookbooks/assets/skills-conceptual-diagram.png`
- `docs/architecture-review-sources/official-examples/claude-cookbooks/assets/prog-disc-1.png`
- `docs/architecture-review-sources/official-examples/claude-cookbooks/assets/prog-disc-2.png`

Key extracted guidance for architecture review:
- Practical API contract for Skills usage: use `beta.messages.create`, provide `container.skills`, and include code-execution tooling when executing skill-backed workflows.
- Skill metadata drives initial discovery; full `SKILL.md` content is loaded on relevance (progressive disclosure illustrated in notebook diagrams).
- Skill package composition shown as `SKILL.md` + supporting docs/scripts, reinforcing modular packaging.
- Versioning guidance is operational: use `latest` for Anthropic-managed skills during development, with explicit pinning strategy for production stability.
- Performance behavior matters for architecture planning: document-generation flows can take material execution time and require resilient task expectations.
- Token/cost optimization pattern: reuse `container.id` when possible and prefer concise prompts that rely on skill expertise.
- Troubleshooting guidance emphasizes compatibility correctness (beta endpoint/tool requirements) and explicit failure recovery steps.

Implication for plugin review:
- We will assess whether the plugin architecture matches the practical runtime contract used by real skill workflows, not only conceptual guidance.
- We will check for explicit versioning and container-reuse policies, since these affect reliability and cost in production usage.

### DOC-006 - Claude Cookbooks: patterns/agents (tree)

Included files analyzed:
- `docs/architecture-review-sources/official-examples/claude-cookbooks/patterns-agents/README.md`
- `docs/architecture-review-sources/official-examples/claude-cookbooks/patterns-agents/basic_workflows.ipynb`
- `docs/architecture-review-sources/official-examples/claude-cookbooks/patterns-agents/evaluator_optimizer.ipynb`
- `docs/architecture-review-sources/official-examples/claude-cookbooks/patterns-agents/orchestrator_workers.ipynb`
- `docs/architecture-review-sources/official-examples/claude-cookbooks/patterns-agents/util.py`
- `docs/architecture-review-sources/official-examples/claude-cookbooks/patterns-agents/prompts/research_lead_agent.md`
- `docs/architecture-review-sources/official-examples/claude-cookbooks/patterns-agents/prompts/research_subagent.md`
- `docs/architecture-review-sources/official-examples/claude-cookbooks/patterns-agents/prompts/citations_agent.md`

Key extracted guidance for architecture review:
- Pattern choice should be explicit and task-fit driven: chaining, parallelization, routing, orchestrator-workers, and evaluator-optimizer each solve different workload shapes.
- The examples explicitly warn they are concept demos, not production code; production hardening is required before operational use.
- Orchestrator-workers is best when subtask decomposition is input-dependent; it adds call overhead and must be justified against latency/cost constraints.
- Structured output contracts are central to multi-agent reliability (examples use XML tags); parsing/validation layers are required to handle malformed or empty responses.
- Worker results need explicit validation and fallback behavior; silent failures are a known failure mode.
- Evaluator-optimizer loops require clear evaluation criteria and refinement value; loop termination and guardrails should be explicit in production.
- Multi-agent prompt design should enforce clear role boundaries, non-overlapping delegation, and bounded subagent counts/tool budgets.
- Execution efficiency controls matter: parallelize independent tasks, stop at diminishing returns, and limit tool-call/source budgets.
- Citation augmentation pattern emphasizes text-integrity invariants: post-processors should add evidence references without mutating report substance.

Implication for plugin review:
- We will assess whether the plugin has production-grade guardrails around chosen agent pattern(s), rather than adopting cookbook flows verbatim.
- We will inspect contract robustness (structured outputs, validators, retries, stop conditions) as core architecture requirements.

### DOC-007 - Define success criteria and build evaluations

Key extracted guidance for architecture review:
- Evaluation architecture should start from explicit success criteria that are specific, measurable, achievable, and relevant.
- Use multidimensional quality targets (task fidelity, consistency, relevance/coherence, tone, privacy, context utilization, latency/cost when applicable).
- Evals should mirror real task distribution and include edge cases; task-specific relevance is prioritized over generic benchmark vanity.
- Prefer automated grading where possible and scale evaluation volume; small high-touch suites alone are insufficient for robust iteration.
- Grading method selection should be pragmatic: code-based first when possible, human grading selectively, LLM grading for nuanced judgments with reliability checks.
- LLM grader design requires explicit rubrics, constrained outputs, and reasoning-before-judgment patterns to improve grading consistency.

Implication for plugin review:
- We will inspect whether architecture-level quality gates are tied to explicit measurable criteria rather than implicit “looks good” judgments.
- We will check that grader strategy is intentional and scalable, not accidental or purely manual.

### DOC-008 - Demystifying evals for AI agents

Key extracted guidance for architecture review:
- Agent-eval systems require clear component boundaries: task, trial, grader, transcript, outcome, eval harness, and agent harness.
- Multi-turn/tool-using agents need evaluation methods beyond simple single-turn checks due to stateful error propagation and non-determinism.
- Effective suites mix grader types (deterministic/model/human) with appropriate scoring strategy (weighted/binary/hybrid).
- Capability and regression eval suites serve different lifecycle functions and should both exist; strong capability tasks can graduate into regression suites.
- Non-determinism must be measured explicitly (e.g., pass@k vs consistency-oriented metrics), not ignored.
- Early practical rollout guidance: start with a small real-failure dataset, then iterate quickly rather than waiting for a massive perfect suite.
- Eval harness reliability is critical: isolate trials in stable environments to avoid shared-state leakage and infrastructure-driven false signals.
- Overly brittle “exact tool sequence” grading is discouraged when outcomes permit valid alternative solution paths.
- Long-term value includes baseline tracking for latency, token usage, cost per task, and error rates to support safer model/agent upgrades.

Implication for plugin review:
- We will treat evaluation infrastructure and environment isolation as first-class architecture concerns, not testing afterthoughts.
- We will explicitly audit whether the plugin's quality system distinguishes capability growth from regression protection.

### DOC-009 - HA MCP reference implementation snapshot

Key extracted guidance for architecture review:
- The implementation explicitly positions Skills and MCP as complementary layers (domain guidance + tool execution), not substitutes.
- Server architecture uses lazy initialization and registry-driven module auto-discovery to keep startup and composition flexible.
- Tool loading is filterable via module-level configuration, enabling reduced surface area for targeted deployments.
- Tool semantics are encoded with MCP annotations (`readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`) and validated by tests.
- Tool-count governance is explicit (runtime ceiling pressure), forcing consolidation and prioritization of high-value tools.
- Multi-transport deployment (stdio, HTTP, SSE, OAuth mode) and client-compatibility OAuth metadata extensions are first-class.
- Reliability architecture includes structured error signaling at MCP protocol layer and async operation tracking primitives.
- Operational observability includes built-in usage logging and startup log collection.
- Test strategy includes unit, E2E workflow suites, and explicit performance baselines for critical tools.

Implication for plugin review:
- We should evaluate a hybrid design where Skills govern planning/quality and MCP handles deterministic Home Assistant execution breadth.
- We should prioritize selective MCP capability adoption (module-filtered) over wholesale import to control complexity and tool-surface risk.

## 3. Source Precedence Rules

Define conflict resolution order once documents are collected.

Proposed (to confirm):
1. Official vendor/platform specifications
2. Internal architecture standards
3. Security/compliance requirements
4. Team best-practice guides
5. Community references/examples

Status: Confirmed and locked for execution

## 4. Extracted Review Criteria

Populate this only after reading shared documents.

| Criterion ID | Domain | Requirement | Source(s) | Criticality | Notes |
|---|---|---|---|---|---|
| CRIT-001 | Architecture strategy | Core design should prefer general mechanisms that improve with additional compute/model capability over narrowly hand-coded heuristics. | DOC-001 | High | Provisional until cross-doc synthesis. |
| CRIT-002 | Modularity | Domain-specific rules should be isolated to configurable/replaceable modules, not embedded in core control flow. | DOC-001 | High | Provisional until cross-doc synthesis. |
| CRIT-003 | Scalability | Critical workflows should support scale-up paths (parallelism, batching, retriable orchestration) rather than fixed-size assumptions. | DOC-001 | Medium | Provisional until cross-doc synthesis. |
| CRIT-004 | Decision quality | Architecture choices should be justified by measurable outcomes/benchmarks, not only intuition about how intelligence "should" work. | DOC-001 | Medium | Provisional until cross-doc synthesis. |
| CRIT-005 | Future-proofing | Interfaces should support evolution (model/tool/provider swaps) with minimal core rewrites. | DOC-001 | Medium | Provisional until cross-doc synthesis. |
| CRIT-006 | Skill packaging | Skill architecture must honor required package contract (`SKILL.md` exact naming; optional `scripts/`, `references/`, `assets/` used for separation of concerns). | DOC-002 | High | Provisional until cross-doc synthesis. |
| CRIT-007 | Activation quality | Frontmatter must provide precise triggerability (`name` kebab-case; `description` includes what + when + realistic trigger phrases). | DOC-002 | High | Provisional until cross-doc synthesis. |
| CRIT-008 | Context efficiency | Apply progressive disclosure: keep primary instructions concise and route detailed material to linked references/assets. | DOC-002 | High | Provisional until cross-doc synthesis. |
| CRIT-009 | Security hardening | Frontmatter and metadata must follow security restrictions (no XML tags in metadata, reserved naming constraints, static safe metadata content). | DOC-002 | High | Provisional until cross-doc synthesis. |
| CRIT-010 | Reliability | Instructions and orchestration should include explicit error handling, recovery guidance, and troubleshooting paths for tool/API failures. | DOC-002 | High | Provisional until cross-doc synthesis. |
| CRIT-011 | Testability | Quality strategy must include trigger tests, functional tests, and baseline comparison metrics; evidence of iteration loop is required. | DOC-002 | High | Provisional until cross-doc synthesis. |
| CRIT-012 | Portability/composability | Design should work across Claude.ai, Claude Code, and API surfaces and avoid assumptions that break coexistence with other skills. | DOC-002 | Medium | Provisional until cross-doc synthesis. |
| CRIT-013 | Operability | Architecture should include monitoring and refinement for under-triggering and over-triggering behavior post-deployment. | DOC-002 | Medium | Provisional until cross-doc synthesis. |
| CRIT-014 | Context governance | `SKILL.md` should remain concise (target under 500 lines) with progressive-disclosure file splitting to preserve context capacity. | DOC-003 | High | Provisional until cross-doc synthesis. |
| CRIT-015 | Reference topology | Skill references should be one level deep from `SKILL.md` to reduce missed-link and navigation failure risk. | DOC-003 | Medium | Provisional until cross-doc synthesis. |
| CRIT-016 | Workflow rigor | Complex tasks should be represented as explicit sequential workflows with checkpoints and feedback loops. | DOC-003 | High | Provisional until cross-doc synthesis. |
| CRIT-017 | Evaluation discipline | Evaluation-first approach required: baseline, explicit scenarios, and iterative refinement from observed failures. | DOC-003 | High | Provisional until cross-doc synthesis. |
| CRIT-018 | Cross-model robustness | Skill behavior should be validated on all intended target models/surfaces before release. | DOC-003 | High | Provisional until cross-doc synthesis. |
| CRIT-019 | Deterministic execution | Prefer executable utility scripts for deterministic operations; scripts must handle errors explicitly and avoid unexplained constants. | DOC-003 | High | Provisional until cross-doc synthesis. |
| CRIT-020 | Safety by verification | High-impact flows should use plan/validate/execute/verify patterns with machine-verifiable intermediate artifacts. | DOC-003 | High | Provisional until cross-doc synthesis. |
| CRIT-021 | Runtime compatibility | Architecture must explicitly account for runtime/package/network differences between Claude surfaces (especially API constraints). | DOC-003 | High | Provisional until cross-doc synthesis. |
| CRIT-022 | Tool addressing | MCP tool invocations should use fully qualified naming (`ServerName:tool_name`) for reliability in multi-server environments. | DOC-003 | Medium | Provisional until cross-doc synthesis. |
| CRIT-023 | Portability hygiene | Paths and file conventions must be cross-platform safe (forward slashes, descriptive filenames, predictable directory layout). | DOC-003 | Medium | Provisional until cross-doc synthesis. |
| CRIT-024 | Instruction UX | Guidance should provide sensible defaults and avoid excessive branch options that degrade execution reliability. | DOC-003 | Medium | Provisional until cross-doc synthesis. |
| CRIT-025 | Verification architecture | Major workflows should include built-in self-verification steps (tests, assertions, visual/output checks) before task completion. | DOC-004 | High | Provisional until cross-doc synthesis. |
| CRIT-026 | Execution staging | Non-trivial changes should follow explicit explore/plan/implement phases with acceptance checks; trivial tasks may bypass planning. | DOC-004 | Medium | Provisional until cross-doc synthesis. |
| CRIT-027 | Input contract quality | Task interfaces should capture scope, source-of-truth references, symptoms, constraints, and success criteria to reduce rework loops. | DOC-004 | High | Provisional until cross-doc synthesis. |
| CRIT-028 | Context operations | Architecture should support context hygiene mechanisms (scoped reads, compaction, reset boundaries) for long-running sessions. | DOC-004 | High | Provisional until cross-doc synthesis. |
| CRIT-029 | Persistent memory design | Persistent instruction files should remain concise/high-signal and delegate contextual specialization to on-demand skills. | DOC-004 | High | Provisional until cross-doc synthesis. |
| CRIT-030 | Deterministic guardrails | Use deterministic enforcement points (hooks/policies) for non-negotiable checks instead of advisory prompt text alone. | DOC-004 | High | Provisional until cross-doc synthesis. |
| CRIT-031 | Permission safety model | Prefer sandbox + scoped allowlists; unrestricted autonomy modes require explicit isolation and threat controls. | DOC-004 | High | Provisional until cross-doc synthesis. |
| CRIT-032 | Investigation isolation | Research/review tasks should be isolatable (e.g., subagent pattern) to prevent pollution of implementation context. | DOC-004 | Medium | Provisional until cross-doc synthesis. |
| CRIT-033 | Scalable automation | Headless/parallel/fan-out operation should use scoped tool permissions and phased rollout to control blast radius. | DOC-004 | Medium | Provisional until cross-doc synthesis. |
| CRIT-034 | Failure-mode resilience | Architecture should proactively mitigate known failure modes: context drift, correction churn, unscoped exploration, and unverifiable outputs. | DOC-004 | High | Provisional until cross-doc synthesis. |
| CRIT-035 | Runtime API correctness | Skill-enabled flows should use the correct runtime API/tool contract (beta message path, skill container, code execution tool requirements). | DOC-005 | High | Provisional until cross-doc synthesis. |
| CRIT-036 | Skill lifecycle policy | Architecture should define explicit skill version policy (managed-latest vs pinned) by environment/stability requirements. | DOC-005 | Medium | Provisional until cross-doc synthesis. |
| CRIT-037 | Session reuse efficiency | Reuse runtime containers/session handles where supported to reduce repeated skill-load overhead and token cost. | DOC-005 | Medium | Provisional until cross-doc synthesis. |
| CRIT-038 | Long-running task robustness | File-generation workflows should include timeout/retry/user-expectation handling for multi-minute operations. | DOC-005 | Medium | Provisional until cross-doc synthesis. |
| CRIT-039 | Pattern-fit selection | Architecture should select agent workflow patterns based on task shape (sequential dependency, independent parallelism, routing specialization, dynamic decomposition, iterative refinement). | DOC-006 | High | Provisional until cross-doc synthesis. |
| CRIT-040 | Production hardening | Cookbook/demo flows must be hardened for production with explicit reliability controls before adoption. | DOC-006 | High | Provisional until cross-doc synthesis. |
| CRIT-041 | Structured contract robustness | Inter-agent contracts should use machine-parseable schemas with robust parsing/validation and malformed-output handling. | DOC-006 | High | Provisional until cross-doc synthesis. |
| CRIT-042 | Failure containment | Worker/orchestrator failures (empty outputs, bad decomposition, parse failures) must trigger explicit fallback/error paths. | DOC-006 | High | Provisional until cross-doc synthesis. |
| CRIT-043 | Eval-loop safety | Evaluator-optimizer loops require explicit pass criteria, iteration bounds, and termination safeguards. | DOC-006 | High | Provisional until cross-doc synthesis. |
| CRIT-044 | Delegation discipline | Subagent delegation should enforce clear task boundaries, minimal overlap, and bounded agent counts aligned to complexity. | DOC-006 | Medium | Provisional until cross-doc synthesis. |
| CRIT-045 | Budget governance | Tool-call/source budgets and stop-at-diminishing-returns controls should be first-class operational constraints. | DOC-006 | Medium | Provisional until cross-doc synthesis. |
| CRIT-046 | Parallel efficiency | Independent subtasks should execute in parallel where safe; sequential processing should be justified when chosen. | DOC-006 | Medium | Provisional until cross-doc synthesis. |
| CRIT-047 | Cost/latency transparency | Architecture should make N+1 call overhead and model-mix tradeoffs explicit for orchestration patterns. | DOC-006 | Medium | Provisional until cross-doc synthesis. |
| CRIT-048 | Evidence post-processing integrity | Citation/evidence augmentation components must preserve original synthesized content and only add attribution metadata. | DOC-006 | Medium | Provisional until cross-doc synthesis. |
| CRIT-049 | Criteria-first quality model | Architecture should define explicit measurable success criteria (SMART-style) before implementation/eval iteration begins. | DOC-007 | High | Provisional until cross-doc synthesis. |
| CRIT-050 | Multidimensional quality coverage | Evaluation should cover relevant quality dimensions (fidelity, consistency, coherence, privacy, context use, operational metrics). | DOC-007 | High | Provisional until cross-doc synthesis. |
| CRIT-051 | Task-distribution realism | Eval datasets should reflect real task distribution and include meaningful edge-case coverage. | DOC-007 | High | Provisional until cross-doc synthesis. |
| CRIT-052 | Scalable grading strategy | Grader mix should prioritize reliable automation and explicit scalability tradeoffs (code, LLM, human calibration). | DOC-007 | High | Provisional until cross-doc synthesis. |
| CRIT-053 | LLM grader reliability | LLM-based graders require precise rubrics, constrained outputs, and consistency-improving prompt design. | DOC-007 | Medium | Provisional until cross-doc synthesis. |
| CRIT-054 | Eval throughput discipline | Architecture should support high-volume evaluation loops rather than sparse manual checks as primary signal. | DOC-007 | Medium | Provisional until cross-doc synthesis. |
| CRIT-055 | Eval system decomposition | The architecture should explicitly model eval system components (task/trial/grader/transcript/outcome/harness). | DOC-008 | High | Provisional until cross-doc synthesis. |
| CRIT-056 | Capability-regression split | Maintain distinct capability and regression suites with clear lifecycle movement between them. | DOC-008 | High | Provisional until cross-doc synthesis. |
| CRIT-057 | Non-determinism-aware metrics | Use reliability-aware metrics for stochastic behavior (e.g., pass@k and consistency-oriented metrics) aligned to product needs. | DOC-008 | High | Provisional until cross-doc synthesis. |
| CRIT-058 | Harness isolation | Eval trials should run in isolated, stable environments to avoid state leakage and infrastructure-induced noise. | DOC-008 | High | Provisional until cross-doc synthesis. |
| CRIT-059 | Outcome-over-procedure grading | Prefer outcome-correctness grading over brittle step-sequence enforcement unless procedural constraints are truly mandatory. | DOC-008 | Medium | Provisional until cross-doc synthesis. |
| CRIT-060 | Eval bootstrap pragmatism | Architecture should allow early eval adoption from real failures with incremental suite growth. | DOC-008 | Medium | Provisional until cross-doc synthesis. |
| CRIT-061 | Ops metric baselining | Track latency, token usage, cost per task, and error rates as part of ongoing eval-regression infrastructure. | DOC-008 | Medium | Provisional until cross-doc synthesis. |
| CRIT-062 | Model-upgrade readiness | Eval infrastructure should enable fast, evidence-based adoption of new models without prolonged manual revalidation. | DOC-008 | Medium | Provisional until cross-doc synthesis. |
| CRIT-063 | Skills+MCP separation of concerns | Architecture should separate decision/policy guidance (Skills) from deterministic system interaction (MCP tools) rather than overloading either layer. | DOC-009 | High | Provisional until cross-doc synthesis. |
| CRIT-064 | Tool surface governance | MCP capabilities should be module-filterable so deployments can minimize exposed tool surface by task profile/risk. | DOC-009 | High | Provisional until cross-doc synthesis. |
| CRIT-065 | Tool semantic annotation discipline | Every tool should declare correct behavior hints (`readOnlyHint` vs `destructiveHint`, plus idempotence/open-world where applicable) and enforce this via tests. | DOC-009 | High | Provisional until cross-doc synthesis. |
| CRIT-066 | Tool count budgeting | Architecture should enforce explicit tool-count budgets and consolidation strategy to preserve client compatibility and usability. | DOC-009 | Medium | Provisional until cross-doc synthesis. |
| CRIT-067 | Multi-transport operability | Runtime should support clear transport/auth modes (stdio/http/sse/oauth) with explicit configuration requirements per mode. | DOC-009 | Medium | Provisional until cross-doc synthesis. |
| CRIT-068 | OAuth client interoperability | OAuth metadata and endpoint behavior should account for practical client interoperability constraints, not only nominal spec compliance. | DOC-009 | Medium | Provisional until cross-doc synthesis. |
| CRIT-069 | Protocol-level error signaling | Tool failures should be signaled in protocol-native form (not plain text only) with structured, actionable error payloads. | DOC-009 | High | Provisional until cross-doc synthesis. |
| CRIT-070 | Async mutation observability | Long-running or async mutations should expose operation IDs/status transitions/timeouts for reliable follow-up and recovery. | DOC-009 | High | Provisional until cross-doc synthesis. |
| CRIT-071 | Operational telemetry baseline | Architecture should include low-overhead usage/performance telemetry suitable for regression detection and optimization loops. | DOC-009 | Medium | Provisional until cross-doc synthesis. |

Suggested domains:
- System boundaries and responsibilities
- Interfaces/contracts
- Data flow and state management
- Security and secrets handling
- Reliability and error handling
- Observability and operability
- Performance and scalability
- Testability and maintainability

## 5. Open Questions / Assumptions

| ID | Type | Question / Assumption | Impact | Owner | Status |
|---|---|---|---|---|---|
| Q-001 | Question | Which domain-specific behaviors are intentionally non-negotiable in this plugin, even if they reduce generality? | High | Ben / Codex | Resolved |
| Q-002 | Question | Which scaling axis matters most for this plugin architecture (latency, throughput, token cost, tool-call volume, or reliability under load)? | High | Ben / Codex | Resolved |
| Q-003 | Question | Which deployment surface is primary for this plugin review target (Claude Code only, Claude.ai, API, or multi-surface parity)? | High | Ben / Codex | Resolved |
| Q-004 | Question | What trigger-quality thresholds are acceptable (false-positive/false-negative activation rate) for this plugin? | Medium | Ben / Codex | Resolved |
| Q-005 | Question | Which model targets are in scope for acceptance testing (Haiku, Sonnet, Opus, and/or specific versions)? | High | Ben / Codex | Resolved |
| Q-006 | Question | Must the reviewed architecture support API runtime constraints (no network / no runtime package install), or is Claude Code runtime the primary target? | High | Ben / Codex | Resolved |
| Q-007 | Question | Which workflows in this plugin are high-stakes and therefore require plan/validate/execute/verify guardrails? | High | Ben / Codex | Resolved |
| Q-008 | Question | What autonomy level is acceptable for this plugin in production (manual approvals, allowlisted commands, sandboxed auto-run, or full unattended mode)? | High | Ben / Codex | Resolved |
| Q-009 | Question | What minimum verification evidence is required before marking work complete (tests, snapshots, lint/build, or domain-specific checks)? | High | Ben / Codex | Resolved |
| Q-010 | Question | Which operations are safe to parallelize/headless, and what tool/permission boundaries must apply in those modes? | Medium | Ben / Codex | Resolved |
| Q-011 | Question | Should production architecture pin specific skill/tool versions, or allow rolling `latest` for managed skills? | Medium | Ben / Codex | Resolved |
| Q-012 | Question | Do we require container/session reuse for cost control in long workflows, and where is that state managed? | Medium | Ben / Codex | Resolved |
| Q-013 | Question | Which agent pattern(s) are in scope for this plugin (routing, orchestrator-workers, evaluator loops), and where are they intentionally excluded? | High | Ben / Codex | Resolved |
| Q-014 | Question | For structured outputs, do we standardize on XML, JSON schema, or both, and what validator/parser guarantees are required? | High | Ben / Codex | Resolved |
| Q-015 | Question | What are the hard caps for iterative loops (max retries/iterations) and failure escalation behavior? | High | Ben / Codex | Resolved |
| Q-016 | Question | Which reliability metric should drive acceptance for this plugin (single-run pass rate, pass@k, consistency-style metric, or a combination)? | High | Ben / Codex | Resolved |
| Q-017 | Question | What trial-isolation guarantees are required in the eval harness (clean FS, clean state, deterministic fixtures, resource quotas)? | High | Ben / Codex | Resolved |
| Q-018 | Question | Do we maintain separate capability and regression suites, and what promotion criteria move tests from one to the other? | Medium | Ben / Codex | Resolved |
| Q-019 | Question | For this plugin, which Home Assistant capabilities should stay in Skills-only guidance versus be exposed as MCP executable tools? | High | Ben / Codex | Resolved |
| Q-020 | Question | What is the maximum acceptable MCP tool surface for this project before usability, reliability, or safety degrades? | High | Ben / Codex | Resolved |
| Q-021 | Question | Should we target stdio-only integration first, or include HTTP/SSE/OAuth transport modes in initial architecture scope? | Medium | Ben / Codex | Resolved |
| Q-022 | Question | Which operations require explicit async operation tracking/status polling semantics (e.g., bulk control, long config updates)? | Medium | Ben / Codex | Resolved |
| Q-023 | Question | Do we want annotation-policy tests (readOnly vs destructive) as a hard quality gate in this plugin's CI? | Medium | Ben / Codex | Resolved |

Status legend:
- Open
- Resolved
- Deferred

Checkpoint references:
- Checkpoint 1 artifact (Phase 0 + Phase 1): `docs/architecture-review-checkpoints/2026-02-21-checkpoint-1-phase-0-1.md`
- Deferred-question decision proposal: `docs/architecture-review-checkpoints/2026-02-21-deferred-question-decision-proposal.md`

### 5a. Decision Outcomes (2026-02-21)

Finalized decisions for questions that were previously deferred:

| ID | Final decision |
|---|---|
| Q-004 | Trigger-quality target: false-positive <= 8%, false-negative <= 10% (recall-leaning due to in-directory plugin usage context). |
| Q-005 | Model scope: Sonnet 4.6 only. |
| Q-010 | Parallel/headless policy: read-only discovery and diagnostics may parallelize; side-effectful operations must remain sequential with explicit confirmation. |
| Q-012 | Not applicable for current target surface (Claude Code plugin runtime); revisit only if API/MCP runtime is introduced. |
| Q-014 | Structured output standard: JSON schema for machine-consumed artifacts, Markdown for human-facing reports; XML not required. |
| Q-015 | Loop/retry caps: max 2 retries per external command; max 3 refinement iterations per stage; then mandatory user escalation. |
| Q-016 | Reliability metric policy: single-run pass rate (primary) plus pass@3 (secondary). |
| Q-017 | Eval isolation baseline: clean workspace snapshot, reset `.claude` state, deterministic fixtures, bounded command/turn/token budgets. |
| Q-018 | Maintain separate capability and regression suites; promote tests after repeated stable passes plus real-incident relevance. |
| Q-020 | MCP tool-surface budget (if adopted): initial cap of 12 tools; expansion requires explicit justification. |
| Q-021 | MCP transport scope (if adopted): stdio-only in initial phase; HTTP/SSE/OAuth deferred. |
| Q-022 | Async tracking requirement (if adopted): operation IDs plus status polling required for >10s operations, bulk multi-entity mutations, and multi-phase partial-failure-risk workflows. |
| Q-023 | Annotation-policy tests (if adopted): enforce read-only vs destructive classification checks as a hard CI gate. |

## 6. Review Plan Draft

Objective:
- Perform a methodical architecture review of the current Claude Code plugin against the loaded guidance corpus (DOC-001..DOC-009), with explicit focus on design quality, functional correctness posture, optimization, and Skills+MCP composition strategy.

Execution gate:
- Do not start the architecture review itself until Ben approves this plan.

### 6.1 Scope And Boundaries

In scope:
- System boundaries and responsibility split (prompt/skill/orchestration/tool layers).
- Skills design quality (triggering, progressive disclosure, instruction architecture).
- MCP integration architecture (tool surface, annotation quality, transport/auth modes, operability).
- Reliability, safety, and verification patterns (error signaling, high-risk operation controls, test/eval strategy).
- Performance and scalability architecture (context budget, tool count budget, latency/cost observability).
- Merge strategy for plugin + HA MCP capabilities (selective adoption plan).

Out of scope:
- Feature-by-feature UX copy polish.
- Low-level coding-style lint concerns unless architecture-significant.
- Full security pentest or production infra hardening audit.

### 6.2 Method And Phases

Phase 0 - Calibration and assumptions lock:
- Resolve or explicitly defer open questions Q-001..Q-023.
- Confirm target runtime surfaces and acceptable autonomy/safety envelope.
- Freeze source precedence for conflict resolution.

Phase 1 - Architecture inventory and boundary map:
- Build the current-state architecture map for the plugin.
- Map control flow: request intake -> reasoning/policy -> tool execution -> verification -> reporting.
- Document explicit interfaces and contracts for skills, prompts, tools, and runtime config.

Phase 2 - Criteria-to-artifact traceability setup:
- Map every criterion CRIT-001..CRIT-071 to concrete code/config/docs artifacts.
- Mark each criterion as `Applicable`, `Partially Applicable`, or `Not Applicable` with justification.

Phase 3 - Deep architecture assessment by domain:
- Evaluate each domain: boundaries, contracts, state flow, safety, reliability, observability, performance, maintainability.
- Record findings with severity, impact, confidence, and evidence references.
- Highlight regressions against official guidance and brittle design areas.

Phase 4 - Skills+MCP composition analysis:
- Compare three options:
1. Skills-heavy with minimal MCP.
2. MCP-heavy with thin skills.
3. Hybrid selective model (expected frontrunner).
- For each option, evaluate quality, safety, latency/cost, maintenance burden, and failure modes.
- Produce candidate MCP tool adoption triage: `Adopt now`, `Adopt later`, `Do not adopt`.

Phase 5 - Evaluation and guardrail architecture:
- Design target eval stack aligned to DOC-007/DOC-008:
1. Capability suite.
2. Regression suite.
3. Grader strategy (code/LLM/human).
4. Non-determinism metrics (pass@k/consistency).
- Define required verification gates for high-impact flows.

Phase 6 - Target-state architecture and roadmap:
- Produce recommended target architecture with rationale.
- Define phased implementation roadmap: near-term, mid-term, long-term.
- Include migration risks, dependencies, and rollback strategies.

### 6.3 Deliverables

Required outputs:
1. Architecture Review Report:
   Includes findings by severity with evidence and criterion mapping.
2. Criteria Compliance Matrix:
   CRIT-001..CRIT-071 status with rationale and gaps.
3. Skills+MCP Decision Log:
   Tool/module-level adoption decisions and reasoning.
4. Target Architecture Proposal:
   Recommended layered design and interface contracts.
5. Execution Roadmap:
   Prioritized remediations and implementation sequence.

### 6.4 Severity / Risk Model

Severity levels:
1. Critical:
   Likely to cause unsafe behavior, major reliability failure, or architecture dead-end.
2. High:
   Significant quality/reliability/maintainability risk that should be fixed before scale-up.
3. Medium:
   Material improvement area with moderate impact or constrained blast radius.
4. Low:
   Optimization/polish opportunity with limited downside.

Scoring convention:
- `Compliant`, `Partially Compliant`, `Non-Compliant`, `Not Applicable`.
- Confidence score per finding: `High`, `Medium`, `Low`.

### 6.5 Traceability Approach

Each finding will include:
1. Finding ID.
2. Criterion IDs impacted.
3. Evidence references (file + line).
4. Risk statement and impact.
5. Recommended remediation.
6. Estimated implementation complexity.

### 6.6 Checkpoints And Cadence

Checkpoint 1 (after Phase 1-2):
- Confirm architecture map completeness and criteria applicability.

Checkpoint 2 (after Phase 3):
- Review top findings and severity calibration before solutioning.

Checkpoint 3 (after Phase 4-5):
- Review Skills+MCP option analysis and eval/guardrail proposal.

Checkpoint 4 (final):
- Approve target architecture and implementation roadmap.

Status: Review execution complete (all planned phases complete)

## 7. Progress Log

| Date | Update | Owner |
|---|---|---|
| 2026-02-21 | Created workplan template and initialized tracking sections. | Codex |
| 2026-02-21 | Logged first source document in inventory (`DOC-001`). | Codex |
| 2026-02-21 | Updated process to hybrid analysis workflow (per-document provisional analysis + final synthesis). | Codex |
| 2026-02-21 | Completed provisional analysis of `DOC-001` and extracted initial architecture criteria/questions. | Codex |
| 2026-02-21 | Reorganized source files: moved `DOC-001` into `best-practices` and normalized filename. | Codex |
| 2026-02-21 | Reorganized newly uploaded guide files, selected canonical copy, and moved it to `official/anthropic-complete-guide-building-skills-for-claude.md`. | Codex |
| 2026-02-21 | Removed duplicate regenerated file after ACL-restricted deletion required elevated permissions. | Codex |
| 2026-02-21 | Completed provisional analysis of `DOC-002` and expanded architecture criteria set (`CRIT-006` to `CRIT-013`). | Codex |
| 2026-02-21 | Fetched and saved official markdown source for Agent Skills best practices as `DOC-003`. | Codex |
| 2026-02-21 | Completed provisional analysis of `DOC-003` and expanded architecture criteria set (`CRIT-014` to `CRIT-024`). | Codex |
| 2026-02-21 | Fetched and saved official markdown source for Claude Code best practices as `DOC-004`. | Codex |
| 2026-02-21 | Completed provisional analysis of `DOC-004` and expanded architecture criteria set (`CRIT-025` to `CRIT-034`). | Codex |
| 2026-02-21 | Added official Anthropic cookbook notebook as `DOC-005` in `official-examples/claude-cookbooks/`. | Codex |
| 2026-02-21 | Downloaded and reviewed all notebook-linked image assets to capture image-only guidance for `DOC-005`. | Codex |
| 2026-02-21 | Completed provisional analysis of `DOC-005` and expanded architecture criteria set (`CRIT-035` to `CRIT-038`). | Codex |
| 2026-02-21 | Downloaded full Anthropic cookbook `patterns/agents` subtree (8 files) as `DOC-006`, including subpages/prompts/notebooks. | Codex |
| 2026-02-21 | Verified `DOC-006` notebooks contain no linked or embedded image outputs requiring separate asset capture. | Codex |
| 2026-02-21 | Completed provisional analysis of `DOC-006` (agent-pattern subtree) and expanded architecture criteria set (`CRIT-039` to `CRIT-048`). | Codex |
| 2026-02-21 | Fetched evaluation-focused sources only (`develop-tests` and `demystifying-evals`) per narrowed scope request. | Codex |
| 2026-02-21 | Confirmed selected eval sources are distinct (not duplicates) and normalized source formats (`.md` for docs page, `.html` for engineering article). | Codex |
| 2026-02-21 | Completed provisional analysis of `DOC-007` and `DOC-008`; expanded architecture criteria set (`CRIT-049` to `CRIT-062`). | Codex |
| 2026-02-21 | Added and analyzed `DOC-009` from local HA MCP codebase snapshot to support Skills+MCP merge evaluation; expanded criteria (`CRIT-063` to `CRIT-071`) and integration questions (`Q-019` to `Q-023`). | Codex |
| 2026-02-21 | Finalized comprehensive review execution plan (scope, phases, deliverables, severity model, traceability, checkpoints) in Section 6. | Codex |
| 2026-02-21 | Executed Phase 0 and Phase 1; persisted Checkpoint 1 output to `docs/architecture-review-checkpoints/2026-02-21-checkpoint-1-phase-0-1.md`. | Codex |
| 2026-02-21 | Synchronized Section 5 open-question statuses to `Resolved`/`Deferred` based on Phase 0 triage and linked the checkpoint artifact for rationale/evidence. | Codex |
| 2026-02-21 | Produced proposed default decisions for all deferred questions in `docs/architecture-review-checkpoints/2026-02-21-deferred-question-decision-proposal.md` to accelerate closure. | Codex |
| 2026-02-21 | Resolved all previously deferred questions (Q-004, Q-005, Q-010, Q-012, Q-014..Q-018, Q-020..Q-023) with user-approved final policies and recorded them in Section 5a. | Codex |
| 2026-02-21 | Executed Phase 2 and published `CRIT-001..CRIT-071` applicability traceability matrix: `docs/architecture-review-checkpoints/2026-02-21-checkpoint-1-phase-2-criteria-traceability-matrix.md`. | Codex |
| 2026-02-21 | Executed Phase 3 deep architecture assessment and published Checkpoint 2 findings with severity calibration: `docs/architecture-review-checkpoints/2026-02-21-checkpoint-2-phase-3-deep-architecture-assessment.md`. | Codex |
| 2026-02-21 | Executed Phase 4 and Phase 5; published Checkpoint 3 option analysis and eval/guardrail architecture: `docs/architecture-review-checkpoints/2026-02-21-checkpoint-3-phase-4-5-composition-and-eval-guardrails.md`. | Codex |
| 2026-02-21 | Executed Phase 6 and published final target architecture plus roadmap (Checkpoint 4): `docs/architecture-review-checkpoints/2026-02-21-checkpoint-4-phase-6-target-architecture-and-roadmap.md`. | Codex |
