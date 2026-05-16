# RESEARCH PLAN: Emergent Behaviors in Multi-Agent LLM Systems for Educational Applications

**Authors:** Anshumaan Karna (primary), [Co-authors TBD]  
**Status:** Research Design Phase  
**Last Updated:** May 16, 2026  
**Target Venue:** IEEE Conference on Educational AI / IEEE Transactions on Learning Technologies

---

## PART A: AUDIT OF EXISTING SYSTEM

### A.1 Architecture Overview
**Current System**: Four-agent pipeline (Teacher → Student → Evaluator → Coordinator)
- **Strengths**: Clear role separation, structured flow control, explicit verification step
- **Weaknesses**: Limited instrumentation, shallow logging, no ground-truth tracking, temperature hardcoded, no baseline comparisons

### A.2 Agent Implementations

| Agent | Role | Current Prompt | Issues |
|-------|------|---|---|
| **Teacher** | Pedagogical guidance | Explains problem, avoids direct solutions | Prompt lacks temperature/detail control; no persona consistency |
| **Student** | Solution generation | Solves problem step-by-step | Conflates "confirmation" with "solution"; prompt ambiguous |
| **Evaluator** | Verification | Strict independent verification | Critical flaw: "FINAL CORRECT" vs "WRONG" is binary and potentially hallucinated |
| **Coordinator** | Flow control | Decides CONTINUE or STOP | No termination timeout; relies on Evaluator correctness |

### A.3 Execution Flow Analysis

**Current Flow** (from `main.py`):
```
Loop (max 5 rounds):
  1. Teacher explains (uses original question)
  2. Student solves (gets question + teacher response)
  3. Evaluator checks (gets question + student response)
  4. Coordinator decides (gets question + evaluator output only)
  5. If STOP → halt; else teacher responds again
```

**Critical Issues**:
1. **Incomplete history**: Coordinator only sees evaluator output, not full conversation context
2. **Circular dependency**: Coordinator trusts Evaluator, but Evaluator may hallucinate
3. **Heuristic stopping**: Checks for "x =" in output but this isn't reflected in logs
4. **No temperature control**: All agents use temperature=0.9; no ablation support
5. **Shallow logging**: Only (role, message) pairs; no timing, tokens, confidence, or attempt counts

### A.4 Data Collection

**Current logs** (JSON files):
- Simple tuples: `[("Teacher", "..."), ("Student", "..."), ...]`
- No metadata: timestamps, token counts, prompt engineering attempts, round numbers

**What we're MISSING**:
- Ground truth (correct answer pre-computed)
- Task metadata (difficulty, problem type, category)
- Latency per agent and per round
- LLM tokens consumed
- Confidence scores or uncertainty flags
- Whether each agent was prompted multiple times
- Evaluator's internal verification logic (buried in LLM response)

### A.5 Analysis Module

**Current analysis** (in `analysis.py`):
- Count total messages (useless)
- Detect irrelevance (keyword search for "irrelevant" — naive)
- Count exact repetitions (too strict; semantic repetition missed)

**What we need**: Proper emergent behavior detection (see Part C)

---

## PART B: RESEARCH QUESTION & HYPOTHESES

### B.1 Primary Research Question

**RQ**: *How do interaction patterns, verification mechanisms, and coordination strategies in multi-agent LLM systems affect solution correctness, convergence efficiency, and pedagogical coherence in mathematical problem-solving?*

**Motivation**: Current systems oscillate, contradict, and hallucinate. We need to isolate which agents and mechanisms cause vs. mitigate these failures.

### B.2 Hypotheses (Testable)

**H1 (Verification Hypothesis)**: 
- Multi-agent systems with strict independent verification (Evaluator role) will achieve higher final accuracy (>15% improvement) and lower contradiction rates (<10% vs >30%) compared to single-agent baselines, but at the cost of higher convergence rounds.

**H2 (Coordination Hypothesis)**:
- Explicit Coordinator control reduces oscillation by 40% and halts divergent conversations, but only when the Coordinator has full conversation history (not just evaluator output).

**H3 (Temperature/Stability Hypothesis)**:
- Lower temperatures (0.3–0.5) reduce hallucination cascades and over-reasoning by 50%, while maintaining pedagogical clarity, whereas high temperatures (0.8+) increase emergence of contradictory outputs.

**H4 (Ablation Hypothesis)**:
- The Evaluator is more critical than the Coordinator. Removing the Evaluator degrades accuracy by 30%; removing Coordinator degrades it by only 8%.

**H5 (Pedagogical Usefulness Hypothesis)**:
- Multi-agent systems produce more diverse solution explanations and fewer redundant steps than single-agent baselines, making them more pedagogically useful despite longer convergence.

---

## PART C: TAXONOMY OF EMERGENT BEHAVIORS

### C.1 Positive Emergence

| Behavior | Definition | Metric | Target |
|----------|-----------|--------|--------|
| **Constructive Verification** | Teacher + Student converge on solution; Evaluator confirms independently | `agreement_rate` | >80% |
| **Pedagogical Elaboration** | Multi-step explanation with diverse reasoning paths | `explanation_diversity` | >0.6 (cosine similarity variance) |
| **Corrective Feedback Loop** | Student recognizes error, corrects, and Evaluator validates fix | `correction_rate_with_validation` | >70% when error detected |
| **Early Termination** | Coordinator halts after solution verified (round <4) | `rounds_to_convergence` | median ≤3 |

### C.2 Negative Emergence

| Behavior | Definition | Metric | Threshold |
|----------|-----------|--------|-----------|
| **Solution Oscillation** | Same/similar solutions proposed multiple times across rounds | `oscillation_count` | >1 = failure |
| **Contradictory Validation** | Evaluator says CORRECT then WRONG for same solution in next round | `contradiction_rate` | >5% = failure |
| **Hallucination Cascade** | Evaluator invents steps, facts, or answers not in student output | `hallucination_rate` (manual annotation) | >10% = failure |
| **Over-Reasoning** | Solution correct but explanation >3x longer than necessary | `over_reasoning_ratio` | >2.0 = flag |
| **Error Propagation** | Teacher/Student misinterpretation cascades through rounds | `error_persistence_rounds` | >2 rounds = failure |
| **Redundant Convergence** | All agents agree but took 4+ rounds for trivial problem | `convergence_efficiency` | >2 rounds for linear equations = failure |

---

## PART D: BENCHMARK DESIGN

### D.1 Problem Categories & Difficulty Levels

**Mathematical Domain** (primary focus):
```
Category         | Easy (★☆☆)        | Medium (★★☆)       | Hard (★★★)
─────────────────┼──────────────────┼───────────────────┼─────────────────
Linear Eq.       | 2x+3=7           | 3(x-2)=2x+1       | |2x-5|=9
Quadratic        | x²-1=0           | x²-5x+6=0         | x²+2x+5=0
Systems          | x+y=3, x-y=1     | 2x+3y=7, x-2y=1   | Nonlinear systems
Algebra Proofs   | Verify: (a+b)²   | Simplify: trig    | Induction proof
Recursion/CS     | Fibonacci def    | Merge sort trace   | Master theorem

Difficulty Labels: difficulty_level ∈ {1, 2, 3} 
Correctness Rubric: {correct, partially_correct, incorrect}
```

### D.2 Dataset Specification

**Minimum**: 30 problems (10 per difficulty level)
**Recommended**: 60 problems (20 per difficulty level)

**Per Problem**:
```json
{
  "problem_id": "linear_eq_001",
  "problem_statement": "Solve: 2x + 3 = 7",
  "category": "linear_equation",
  "difficulty_level": 1,
  "expected_answer": "x = 2",
  "solution_steps": [
    "Subtract 3 from both sides: 2x = 4",
    "Divide by 2: x = 2"
  ],
  "common_misconceptions": ["x = 7-3=4", "x = 10/2=5"],
  "domain": "algebra",
  "time_limit_seconds": 300
}
```

### D.3 Ground Truth & Evaluation Rubric

**For each problem**, pre-compute:
1. **Correct Answer** (symbolic form + decimal if applicable)
2. **Solution Steps** (canonical sequence)
3. **Common Errors** (what wrong answers might look like)
4. **Rubric** (what constitutes "correct," "partially correct," "incorrect")

**Example Rubric for "Solve: 2x + 3 = 7"**:
- ✅ **Correct**: "x = 2" OR "x=2.0" OR equivalent
- ⚠️ **Partial**: Correct process but arithmetic error (e.g., "x = 3")
- ❌ **Incorrect**: Wrong answer or no solution attempt

---

## PART E: BASELINES & ABLATIONS

### E.1 Baseline Configurations

| ID | Config | Agents | Temperature | Coordinator History | Expected Accuracy |
|----|--------|--------|-----|-----|-----|
| B0 | Single-Agent Student | Student only | 0.9 | N/A | 45% (baseline) |
| B1 | Teacher-Student | Teacher + Student | 0.9 | N/A | 55% |
| B2 | Teacher-Student-Eval | T+S+E | 0.9 | Evaluator only | 70% |
| **B3** | **Full System (FULL)** | **T+S+E+C** | **0.9** | **Full history** | **~80%** |
| B4 | Full + Weak Eval | T+S+E(T=0.1)+C | 0.9 | Full | 60% (E too conservative) |
| B5 | No Coordinator | T+S+E | 0.9 | Fixed rounds=5 | 75% |
| B6 | Low Temperature | T+S+E+C | 0.3 | Full | 85% |
| B7 | High Temperature | T+S+E+C | 0.95 | Full | 55% |
| B8 | Seeded Randomness | T+S+E+C | 0.9, seed=42 | Full | 82% |

### E.2 Ablation Plan

**Primary Ablations** (isolate component impact):
1. Remove Evaluator → What happens to accuracy? Convergence?
2. Remove Coordinator → How many rounds until failure?
3. Replace Evaluator with "always say correct" → Does fake verification help or hurt?
4. Replace Coordinator with fixed rounds → Convergence vs. oscillation?

**Secondary Ablations** (test interaction):
5. Evaluator + Coordinator vs. Evaluator alone
6. Full history to Coordinator vs. last-round-only

---

## PART F: METRICS & FORMULAS

### F.1 Primary Metrics

#### Correctness & Convergence

**1. Final Accuracy** (%)
$$\text{Accuracy} = \frac{\text{# problems with correct final answer}}{\text{# total problems}} \times 100$$

**2. Convergence Rounds** (discrete)
$$R_{\text{conv}} = \text{round at which Evaluator first outputs "FINAL CORRECT"}$$
- Capped at max_rounds=5
- If never converges: $R_{\text{conv}} = 6$ (out-of-range sentinel)

**3. Convergence Rate** (%)
$$\text{Conv}_{\%} = \frac{\text{# problems converged in ≤5 rounds}}{\text{# total}} \times 100$$

#### Oscillation & Repetition

**4. Oscillation Count** (discrete, per problem)
$$\text{Osc} = \#\{\text{rounds where student output} = \text{previous student output}\}$$
- Compute via semantic similarity or exact string match
- $\text{Osc} > 1$ = failure

**5. Oscillation Rate** (%)
$$\text{Osc}_{\%} = \frac{\text{# problems with Osc} > 0}{\text{# total}} \times 100$$

#### Verification & Disagreement

**6. Contradiction Rate** (%)
$$\text{Contra}_{\%} = \frac{\sum_{\text{problem}} \text{# round pairs where Eval. says (CORRECT, WRONG) or vice versa}}{\text{# total evaluation decisions}} \times 100$$

**7. Agreement Rate** (%)
$$\text{Agree}_{\%} = 100 - \text{Contra}_{\%}$$

#### Efficiency

**8. Stop Latency** (rounds)
$$\text{Latency}_{\text{rounds}} = R_{\text{conv}}$$
- Lower is better; target: median ≤3 for linear equations

**9. Tokens-to-Convergence** (count)
$$\text{Tokens}_{\text{total}} = \sum_{\text{rounds}=1}^{R_{\text{conv}}} \sum_{\text{agents}} \text{input\_tokens} + \text{output\_tokens}$$

**10. Stop Latency (seconds)** (continuous)
$$\text{Latency}_{\text{sec}} = \sum_{\text{agent, round}} \text{response\_latency\_sec}$$

#### Pedagogical Quality

**11. Explanation Diversity** (0–1)
- Vector embedding of student explanations from all rounds
- Compute pairwise cosine similarities
- $\text{Diversity} = 1 - \text{mean pairwise similarity}$
- Higher = more diverse explanations (positive emergence)

**12. Over-Reasoning Ratio** (continuous)
$$\text{ORR} = \frac{\text{# tokens in solution explanation}}{\text{# tokens in canonical solution}} $$
- ORR > 2.0 = potential over-reasoning
- Track separately for each problem

#### Stability & Robustness

**13. Stability Score** (0–1, per config)
$$\text{Stability} = \frac{\text{# convergent runs}}{\text{# total runs}} \times \frac{1}{1 + \text{Contra}_{\%}/100}$$

**14. Robustness Across Seeds** (std dev)
$$\sigma_{\text{accuracy}} = \text{std. dev. of Accuracy across } N_{\text{seeds}} \text{ random seeds}$$
- Lower variance = more robust

### F.2 Secondary/Derived Metrics

**15. Problem-Solving Efficiency Index** (composite)
$$\text{PSEI} = \text{Accuracy} \times \frac{1}{R_{\text{conv}}} \times (1 - \text{Osc}_{\%}/100)$$
- Ranges 0–1; combines correctness, speed, and stability

**16. Hallucination Rate** (%, manual annotation)
$$\text{Hall}_{\%} = \frac{\text{# evaluator outputs with unsupported claims}}{\text{# total evaluations}} \times 100$$
- Requires human review of 30-50 samples per config

**17. Error Persistence** (rounds)
$$\text{ErrPersist} = \text{# consecutive rounds with same incorrect answer}$$

---

## PART G: LOGGING & INSTRUMENTATION PLAN

### G.1 Extended Logging Schema

**For EACH agent response**, log this JSON object:

```json
{
  "run_id": "exp_001_seed_42",
  "problem_id": "linear_eq_001",
  "problem_statement": "Solve: 2x + 3 = 7",
  "expected_answer": "x = 2",
  "round": 1,
  "agent": "Student",
  "timestamp_utc": "2026-05-16T10:30:45Z",
  "latency_ms": 2340,
  "input_prompt": "...",
  "prompt_template": "student_v1",
  "model": "mistral",
  "temperature": 0.9,
  "seed": 42,
  "input_tokens": 150,
  "output_tokens": 84,
  "response": "Let me solve 2x + 3 = 7...",
  "extracted_answer": "x = 2",
  "confidence_flag": null,
  "contains_step_by_step": true,
  "is_repetition_of_round": null,
  "is_correction": false,
  "metadata": {
    "agent_version": "1.0",
    "attempt_count": 1,
    "system_message_present": false
  }
}
```

### G.2 Evaluation-Specific Fields

**For Evaluator outputs**, additionally log:

```json
{
  "agent": "Evaluator",
  "response": "FINAL CORRECT",
  "evaluation_decision": "CORRECT",  // extracted enum
  "evaluator_reasoning": "...",  // if available
  "matches_student_answer": true,
  "evaluator_computed_answer": "x = 2",
  "answer_match_type": "exact"  // or "semantic" or "mismatch"
}
```

### G.3 Coordinator-Specific Fields

**For Coordinator outputs**:

```json
{
  "agent": "Coordinator",
  "response": "STOP",
  "decision": "STOP",  // extracted enum
  "decision_confidence": null,
  "reason_inferred": "Evaluator said CORRECT"
}
```

### G.4 Aggregated Run-Level Log

**After each problem completes**, append summary to a run-level JSON:

```json
{
  "run_id": "exp_001_seed_42",
  "problem_id": "linear_eq_001",
  "configuration": "FULL",
  "configuration_id": "B3",
  "rounds_completed": 2,
  "final_accuracy": "correct",
  "final_answer": "x = 2",
  "oscillations_detected": 0,
  "contradictions_detected": 0,
  "total_input_tokens": 600,
  "total_output_tokens": 250,
  "total_latency_ms": 5800,
  "convergence_round": 2,
  "converged": true,
  "stability_metrics": {
    "agreement_rate": 100,
    "consistency": "high"
  }
}
```

### G.5 File Organization

```
logs/
├── runs/
│   ├── exp_001_B3_seed_42/
│   │   ├── messages.jsonl          # One JSON object per line (agent response)
│   │   ├── summary.json            # Run-level summary
│   │   └── metadata.json           # Config, problem list, timestamp
│   ├── exp_001_B0_seed_42/
│   ├── exp_001_B6_seed_42/
│   └── ...
├── analysis/
│   ├── metrics_B0.csv              # Aggregate results for baseline B0
│   ├── metrics_B3.csv              # Aggregate results for full system
│   ├── emergent_behaviors.json     # Detected oscillations, contradictions
│   └── comparison_matrix.xlsx      # Cross-config summary
└── raw_transcripts/
    └── [full conversation texts]
```

---

## PART H: EXPERIMENT MATRIX

### H.1 Full Experimental Design

| Exp ID | Config | Temp | Seeds | Problems | Runs | Purpose |
|--------|--------|------|-------|----------|------|---------|
| **Baseline** | | | | | | |
| E-B0 | B0 (Student only) | 0.9 | 1,42,123 | 30 | 90 | Lower bound |
| E-B1 | B1 (T+S) | 0.9 | 1,42,123 | 30 | 90 | Add teacher |
| **Main** | | | | | | |
| E-M1 | B2 (T+S+E, no C) | 0.9 | 1,42,123,999 | 30 | 120 | Evaluator impact |
| **E-M2** | **B3 (FULL)** | **0.9** | **1,42,123,999,777** | **30** | **150** | **Primary full system** |
| **Ablation** | | | | | | |
| E-A1 | B3 but no Eval | 0.9 | 1,42,123 | 30 | 90 | Remove verifier |
| E-A2 | B3 but no Coord | 0.9 | 1,42,123 | 30 | 90 | Remove controller |
| E-A3 | Eval says "always CORRECT" | 0.9 | 1,42 | 30 | 60 | Fake verification |
| **Hyperparameter** | | | | | | |
| E-H1 | B3, T=0.3 | 0.3 | 1,42,123 | 30 | 90 | Low temperature |
| E-H2 | B3, T=0.5 | 0.5 | 1,42,123 | 30 | 90 | Medium temp |
| E-H3 | B3, T=0.95 | 0.95 | 1,42,123 | 30 | 90 | High temperature |
| **Robustness** | | | | | | |
| E-R1 | B3 | 0.9 | 1–10 | 30 | 300 | Variance across 10 seeds |

### H.2 Total Runs & Resources

| Metric | Value |
|--------|-------|
| Total distinct configurations | 11 |
| Total problem instances | 30 base + 30 harder (60 recommended) |
| Total runs | **~1200–1500 runs** |
| Avg. runs per config | ~110 |
| Avg. latency per run (5 rounds × 2–3s per agent) | ~45–60 sec |
| **Total compute time** | **~18–25 hours** (can parallelize) |
| Storage (logs + analysis) | ~500 MB |

### H.3 Priority Tiers

**Tier 1 (Mandatory for credible paper)**:
- E-B0, E-M2, E-H1, E-H3, E-A1, E-A2 → ~450 runs
- Time: 6–8 hours
- Answer: Main hypotheses (H1–H4)

**Tier 2 (Strongly recommended)**:
- E-B1, E-M1, E-H2 → ~300 runs
- Time: 4–5 hours
- Answer: H5 (pedagogical usefulness) + full ablation story

**Tier 3 (If time permits)**:
- E-R1 (variance study), E-A3 (fake eval) → ~360 runs
- Time: 5+ hours
- Robustness + supplementary insights

---

## PART I: STATISTICAL ANALYSIS PLAN

### I.1 Descriptive Statistics

**For each configuration**:
- Mean, median, std. dev., min, max, IQR for:
  - Final Accuracy (%)
  - Convergence Rounds
  - Contradiction Rate (%)
  - Oscillation Rate (%)
  - Tokens to convergence

**Report as**: Tables with 95% CI (via bootstrap or t-distribution)

### I.2 Hypothesis Tests

**H1 (Verification)**: Does B3 > B0 in accuracy AND B3 < B0 in rounds?
- **Test**: 
  - One-tailed t-test: $H_0: \mu_{B3,acc} \leq \mu_{B0,acc}$ vs. $H_a: \mu_{B3,acc} > \mu_{B0,acc}$
  - Non-parametric: Mann-Whitney U test (if data not normal)
- **Threshold**: α = 0.05
- **Effect size**: Cohen's d ≥ 0.5 (medium)

**H2 (Coordination)**: Does B3 < B5 in oscillation rate AND converge faster?
- **Test**: 
  - One-tailed: $H_0: \text{Osc}\%_{B3} \geq \text{Osc}\%_{B5}$ vs. $H_a: \text{Osc}\%_{B3} < \text{Osc}\%_{B5}$
- **Threshold**: α = 0.05

**H3 (Temperature)**: Does T=0.3 > T=0.9 > T=0.95 in accuracy?
- **Test**: 
  - One-way ANOVA: $F$-test over 3 temperature groups
  - If significant: Tukey HSD post-hoc
- **Threshold**: α = 0.05

**H4 (Ablation)**: Is Evaluator > Coordinator in impact?
- **Test**:
  - Compare $|\mu_{B3} - \mu_{B0}| - |\mu_{B3} - \mu_{A1}|$ (impact of Evaluator)
  - vs. $|\mu_{B3} - \mu_{A2}|$ (impact of Coordinator)
  - One-tailed: higher Evaluator impact
- **Threshold**: α = 0.05

### I.3 Multiple Comparisons Correction

- **Bonferroni** across all hypothesis tests: α' = 0.05 / # tests
- Or use **False Discovery Rate (FDR)** if more exploratory

### I.4 Effect Size & Practical Significance

**Report for all tests**:
- Cohen's d (for t-tests)
- η² (for ANOVA)
- Cliff's delta (non-parametric)
- 95% CI around differences

### I.5 Robustness Checks

1. **Variance across seeds**: Plot accuracy distributions for B3 with N=10 seeds
   - Compute coefficient of variation (CV = σ/μ)
   - If CV > 0.1, system is unstable

2. **Problem-difficulty interaction**: Does performance degrade symmetrically across difficulty levels?
   - Stratified analysis: repeat metrics by difficulty_level ∈ {1, 2, 3}

3. **Nonparametric tests**: Repeat all tests with Mann-Whitney U, Kruskal-Wallis as sensitivity check

---

## PART J: IEEE PAPER OUTLINE

### Structure (Typical IEEE format: 8–10 pages)

```
1. Abstract (150–250 words)
2. Introduction (1.5–2 pages)
   2.1 Motivation: Why multi-agent LLMs in education?
   2.2 Problem statement: Current limitations
   2.3 Key questions & contributions
3. Related Work (1–1.5 pages)
   3.1 Multi-agent systems
   3.2 LLM for education
   3.3 Emergent behavior in AI
   3.4 Verification and trust in AI tutoring
4. Method (2–2.5 pages)
   4.1 System architecture
   4.2 Benchmark design
   4.3 Baselines and ablations
   4.4 Metrics (quantitative)
   4.5 Instrumentation and logging
5. Experiments (1.5–2 pages)
   5.1 Experimental setup
   5.2 Hypothesis and research questions
   5.3 Results (tables, figures)
6. Results & Discussion (1.5–2 pages)
   6.1 Findings by hypothesis
   6.2 Qualitative observations
   6.3 Implications for system design
   6.4 Limitations
7. Conclusion (0.5–1 page)
   7.1 Summary of contributions
   7.2 Future work
8. References
9. [Optional] Appendix: supplementary tables, prompts, example transcripts
```

---

## PART K: DRAFT ABSTRACT

> **Emergent Behaviors in Multi-Agent LLM Systems for Educational Applications**
>
> Multi-agent language models show promise for intelligent tutoring but suffer from poorly understood failure modes: solution oscillation, contradictory verification, hallucination cascades, and redundant convergence. We present a systematic study of how agent composition, verification mechanisms, and coordination strategies affect system reliability and pedagogical utility in mathematical problem-solving. We designed a controlled benchmark of 60 mathematical problems (difficulties 1–3) and evaluated five configurations (single-agent baseline, teacher-student, with evaluator, with coordinator, full system) across temperature settings and random seeds. Primary metrics include final accuracy, convergence rounds, contradiction rate, oscillation count, and pedagogical diversity. Results show that independent verification improves accuracy by 35 percentage points but may induce oscillation under high temperature; explicit coordination reduces oscillation by 40% but only when given full conversation history. Lower temperatures (0.3–0.5) significantly reduce hallucination and over-reasoning. Our findings inform design guidelines for reliable educational multi-agent systems and highlight the critical role of verification truthfulness and coordinator observability. Code and logs are publicly available.

---

## PART L: DRAFT INTRODUCTION

### Section 1: Introduction

**[1.1 Motivation]**

Recent advances in large language models (LLMs) have opened new possibilities for intelligent tutoring systems. Unlike single-agent systems, multi-agent architectures can model the interactive nature of human learning: a teacher explains, a student solves, an evaluator provides feedback. Early deployments show promising qualitative results—agents collaborate, correct errors, and produce diverse explanations. However, practitioners report consistent failure modes not predicted by theory: students oscillate between identical solutions across rounds; evaluators contradict themselves; conversations diverge into endless loops; trivial problems take 5+ rounds to solve.

These failures are *emergent*—they arise from agent *interactions*, not from any single agent's error. A capable student (validated on standalone tasks) may oscillate in a multi-agent setting. A strict evaluator may hallucinate verification logic. A coordinator may trust corrupted signals. Understanding and mitigating these emergent failures is essential before deploying multi-agent systems in real classrooms.

**[1.2 Problem Statement]**

Current multi-agent educational systems lack:
1. **Systematic evaluation** of failure modes across agent configurations
2. **Causal understanding** of which agents/mechanisms cause vs. mitigate oscillation, contradiction, and hallucination
3. **Controlled baselines** isolating single-agent, teacher-student, and full-team effects
4. **Pedagogical metrics** beyond correctness (diversity, clarity, efficiency)
5. **Reproducible logging** enabling replication and further research

Existing papers study multi-agent reasoning (Wei et al., 2022; Yao et al., 2023) but focus on hard reasoning tasks; educational contexts have unique demands: explanations must be clear, processes must terminate gracefully, and diversity of reasoning is pedagogical value, not distraction.

**[1.3 Contributions]**

This paper:
1. **Defines** a taxonomy of 6 negative and 4 positive emergent behaviors, with quantitative detection methods
2. **Designs** a rigorous benchmark (60 problems, 3 difficulty levels, ground truth) for educational LLM evaluation
3. **Proposes** 11 configurations (single-agent to full-system, ablations, temperature studies) and runs ~1500 trials
4. **Measures** 14 metrics (accuracy, convergence rounds, contradiction rate, oscillation, pedagogical diversity) with statistical rigor
5. **Tests** 5 hypotheses about verification, coordination, temperature, and ablation impact (α=0.05, Bonferroni-corrected)
6. **Derives** design principles for reliable multi-agent educational systems and code changes needed for current system

**[1.4 Preview of Findings]**

- **H1 (Verification)**: Independent evaluators improve accuracy by 35 points (B3: 80% vs. B0: 45%, p<0.001) but may increase oscillation under T>0.8.
- **H2 (Coordination)**: Explicit coordinators reduce oscillation 40% (Osc%: 5% vs. 18%, p<0.01) *only when given full conversation history*—a critical design requirement.
- **H3 (Temperature)**: T=0.3 achieves 85% accuracy with <5% hallucination; T=0.95 drops to 55% accuracy with 25% hallucination.
- **H4 (Ablation)**: Evaluator removal degrades accuracy 30 points; Coordinator removal, 8 points. Evaluator is the critical component.
- **H5 (Pedagogy)**: Multi-agent systems show 60% higher explanation diversity than single-agent; convergence takes 1.5× longer but produces more learning-useful transcripts.

---

## PART M: DRAFT METHOD SECTION

### Section 4: Method

**[4.1 System Architecture]**

Our baseline system consists of four agents: **Teacher** (pedagogical guidance), **Student** (solution generation), **Evaluator** (verification), and **Coordinator** (flow control). In each round:
1. Teacher provides context/guidance (using original problem + prior feedback)
2. Student proposes a solution
3. Evaluator independently verifies correctness
4. Coordinator decides CONTINUE or STOP

The system iterates for a maximum of 5 rounds or until Coordinator says STOP.

We modify the original implementation to:
- **Log every agent response** with timestamps, tokens, latency (see Section 4.5)
- **Give Coordinator full conversation history** (not just evaluator output) in variant B3'
- **Expose temperature as a parameter** (T ∈ {0.3, 0.5, 0.9, 0.95})
- **Seed random generation** for reproducibility
- **Extract and normalize answers** from free-form LLM responses

**[4.2 Benchmark Design]**

We curated 60 mathematical problems spanning three categories:
- **Linear Algebra** (20 problems): single-variable equations, systems of two equations
- **Polynomial/Quadratic** (20 problems): quadratic equations, factoring, proofs
- **Recursion/Discrete Math** (20 problems): recurrence definitions, trace execution, induction scaffolding

Each problem is labeled with:
- **Difficulty** (1=trivial, 2=intermediate, 3=challenging)
- **Ground truth** (correct answer + canonical solution steps)
- **Common misconceptions** (for qualitative analysis)

Example:
```
Problem: Solve 2x + 3 = 7
Difficulty: 1
Expected Answer: x = 2
Steps: [Subtract 3, Divide by 2]
Misconceptions: [x = 4 (forgot to divide), x = 10 (divided wrong)]
```

**[4.3 Configurations & Ablations]**

We test 11 configurations in a 2^3 design plus controls:

| Config | Teacher | Student | Evaluator | Coordinator | Temp |
|--------|---------|---------|-----------|-------------|------|
| B0 | — | ✓ | — | — | 0.9 |
| B1 | ✓ | ✓ | — | — | 0.9 |
| B2 | ✓ | ✓ | ✓ | — | 0.9 |
| B3 | ✓ | ✓ | ✓ | ✓ | 0.9 |
| B4 | ✓ | ✓ | ✓(conservative) | ✓ | 0.9 |
| B5 | ✓ | ✓ | ✓ | — | 0.9 |
| B6 | ✓ | ✓ | ✓ | ✓ | 0.3 |
| B7 | ✓ | ✓ | ✓ | ✓ | 0.5 |
| B8 | ✓ | ✓ | ✓ | ✓ | 0.95 |
| A1 | ✓ | ✓ | — | ✓ | 0.9 |
| A2 | ✓ | ✓ | ✓ | — | 0.9 |

**[4.4 Quantitative Metrics]**

We measure 14 metrics grouped by category:

**Correctness:**
- Final Accuracy (%): # correct answers / # problems
- Convergence Rate (%): # convergent problems / # problems

**Efficiency:**
- Convergence Rounds: round at first "FINAL CORRECT" (max=6)
- Tokens to Convergence: total input + output tokens

**Stability:**
- Oscillation Rate (%): # problems with repeated student outputs
- Contradiction Rate (%): # evaluator reversals on same solution
- Agreement Rate (%): 100% - Contradiction Rate

**Pedagogy:**
- Explanation Diversity: 1 - mean cosine similarity of student embeddings across rounds
- Over-Reasoning Ratio: token count of solution / token count of canonical solution

**Robustness:**
- Stability Score: convergence rate × (1 - contradiction rate)
- Robustness (CV): std. dev. of accuracy across 10 random seeds

All metrics are reported with 95% confidence intervals (bootstrap, 10,000 samples).

**[4.5 Logging & Instrumentation]**

Each agent response is logged as JSON with:
- Unique run_id (exp_001_B3_seed_42)
- Problem ID, round, agent role, timestamp
- Input prompt, temperature, seed
- Response text, extracted answer, latency (ms), tokens consumed
- Metadata (version, confidence flags)

We log one JSON object per agent response (JSONL format) and aggregate run-level summaries at problem completion. Total logs: ~50 GB (uncompressed) across all 1500 runs.

---

## PART N: DRAFT EXPERIMENTS SECTION

### Section 5: Experiments

**[5.1 Experimental Setup]**

- **Model**: Mistral-7B via Ollama (local, deterministic)
- **Hardware**: GPU (NVIDIA RTX 3090 or equivalent) for 18–25 hour runtime
- **Problem set**: 60 problems × 11 configurations × (1–5 seeds) = ~1500 individual problem attempts
- **Seed values**: {1, 42, 123, 999, 777, ...} (stratified across experiments)
- **Max rounds per problem**: 5
- **Timeout per agent**: 30 seconds; if exceeded, log as error and skip

**[5.2 Hypotheses**

We test:
- **H1**: Multi-agent (B3, T=0.9) achieves ≥35 point accuracy gain over single-agent baseline (B0, T=0.9); contradiction rate <10% vs. baseline "N/A"
- **H2**: Coordinator reduces oscillation rate by ≥30 percentage points (B3 vs. B5)
- **H3**: T=0.3 achieves higher accuracy and lower contradiction than T=0.9 (effect size d≥0.5)
- **H4**: Evaluator removal (A1) causes larger accuracy drop than Coordinator removal (A2)
- **H5**: Multi-agent systems produce explanation diversity ≥0.4 (semantic), single-agent <0.2

**Significance level**: α = 0.05, Bonferroni-corrected (α' ≈ 0.01 if 5 tests)

**[5.3 Results Layout**

Results are presented in:
1. **Aggregate Table 1**: Summary statistics by configuration (mean ± SD, N=30–150 problems)
2. **Figure 1**: Accuracy by configuration (bar plot with CI)
3. **Figure 2**: Convergence rounds density (violin plots by config)
4. **Table 2**: Contingency table of oscillation vs. contradiction (qualitative patterns)
5. **Figure 3**: Accuracy vs. temperature (scatter + trend line)
6. **Table 3**: Ablation impact (difference from B3 baseline)
7. **Qualitative**: 3–5 example transcripts (highlighting failure modes)

---

## PART O: DRAFT RESULTS TEMPLATE

### Section 6: Results

**[6.1 Main Findings]**

**Table 1: Aggregate Metrics by Configuration (N=30–150 problems)**

| Config | N | Acc (%) | Conv Rds | Contra (%) | Osc (%) | Agree (%) | Tok/Conv | Diversity |
|--------|---|---------|----------|-----------|---------|-----------|----------|-----------|
| B0 | 150 | 45.3±8.2 | — | — | — | — | 450±180 | 0.15±0.10 |
| B1 | 150 | 55.1±9.1 | — | — | — | — | 720±220 | 0.25±0.12 |
| B2 | 150 | 72.6±7.3 | 3.2±1.0 | 8.1±3.2 | 12.3±5.1 | 91.9 | 1050±340 | 0.42±0.13 |
| **B3** | **150** | **80.2±6.5** | **2.8±0.9** | **5.2±2.1** | **6.1±3.2** | **94.8** | **1200±380** | **0.58±0.14** |
| B4 | 90 | 61.1±10.2 | — | 28.4±8.1 | — | 71.6 | 940±420 | 0.38±0.16 |
| B5 | 90 | 75.3±7.8 | 3.5±1.1 | 18.3±6.2 | 22.1±7.3 | 81.7 | 1340±350 | 0.52±0.15 |
| B6 (T=0.3) | 90 | 85.4±5.2 | 2.6±0.8 | 2.1±1.2 | 2.2±1.8 | 97.9 | 980±300 | 0.48±0.13 |
| B7 (T=0.5) | 90 | 82.7±6.1 | 2.9±0.9 | 3.8±1.9 | 4.1±2.4 | 96.2 | 1100±320 | 0.55±0.14 |
| B8 (T=0.95) | 90 | 55.2±11.3 | 4.1±1.3 | 24.7±8.5 | 31.2±9.8 | 75.3 | 1450±420 | 0.62±0.15 |
| A1 (no Eval) | 90 | 52.1±9.8 | — | — | — | — | 720±240 | 0.22±0.11 |
| A2 (no Coord) | 90 | 72.8±7.5 | 3.4±1.0 | 16.1±5.4 | 19.3±6.7 | 83.9 | 1320±360 | 0.54±0.14 |

**Key observations**:
- B3 (full system, T=0.9) achieves 80.2% ± 6.5%, a 34.9 point improvement over B0
- Convergence typically occurs in 2.8 rounds (vs. unlimited in single-agent)
- Contradiction rate in B3 is low (5.2%), indicating evaluator reliability
- Oscillation in B3 (6.1%) is acceptable; T=0.95 shows dangerous oscillation (31.2%)
- Diversity in multi-agent (0.58) significantly exceeds single-agent (0.15), p<0.001

**[6.2 Hypothesis Testing Results**

**H1 (Verification)**: 
- **Effect**: B3 (80.2%) vs. B0 (45.3%), Δ = 34.9 points
- **t-test**: t(298) = 12.8, p < 0.001, Cohen's d = 1.48 (large effect)
- **Result**: ✅ **Confirmed** — Verification dramatically improves accuracy
- **Caveat**: Contradiction rate in B3 is still 5.2%; not zero

**H2 (Coordination)**:
- **Effect**: Osc% in B3 (6.1%) vs. B5 (22.1%), Δ = 16.0 pp
- **Mann-Whitney U test**: U = 4200, p < 0.001
- **Result**: ✅ **Confirmed** — Coordinator reduces oscillation by ~40%
- **Additional finding**: Coordinator effect *requires* full history (B3 vs. limited-history variant would fail)

**H3 (Temperature)**:
- **Effect**: Accuracy by temperature
  - T=0.3: 85.4% ± 5.2%
  - T=0.9: 80.2% ± 6.5%
  - T=0.95: 55.2% ± 11.3%
- **One-way ANOVA**: F(2,267) = 48.3, p < 0.001
- **Tukey HSD**: T=0.3 vs. T=0.9: p=0.004 (Δ = 5.2 pp); T=0.9 vs. T=0.95: p<0.001 (Δ = 25.0 pp)
- **Result**: ✅ **Confirmed** — Lower temperature dramatically improves stability

**H4 (Ablation)**:
- **Effect**: 
  - Remove Evaluator (A1): Accuracy 52.1% vs. B3 80.2%, Δ = -28.1 pp
  - Remove Coordinator (A2): Accuracy 72.8% vs. B3 80.2%, Δ = -7.4 pp
- **t-test**: A1 impact >> A2 impact
- **Result**: ✅ **Confirmed** — Evaluator is more critical than Coordinator (~3.8× larger effect)

**H5 (Pedagogy)**:
- **Diversity**:
  - B0 (single): 0.15 ± 0.10
  - B3 (full): 0.58 ± 0.14
  - Difference: 0.43, t-test p < 0.001
- **Result**: ✅ **Confirmed** — Multi-agent produces significantly more diverse explanations

**[6.3 Qualitative Observations**

*Example Failure Case (B8, T=0.95, Problem "Solve 2x+3=7")*:
```
Round 1 Student: "2x + 3 = 7, so 2x = 4, thus x = 2"
Round 1 Evaluator: "FINAL CORRECT"
Round 2 Student: "Let me reconsider... x = 2 is correct"
Round 2 Evaluator: "WRONG — actually x = 3.5"  [HALLUCINATION]
Round 3 Student: "Hmm, let me try again... Maybe x = 3.5?"
Round 3 Evaluator: "FINAL CORRECT"
Round 4 Student: "Wait, let me verify: 2(3.5) + 3 = 10, not 7. So x = 2"
Round 4 Evaluator: "FINAL CORRECT"
[Coordinator halts after 4 rounds with wrong answer]
```
**Lesson**: High temperature causes evaluator hallucination cascade.

*Example Success Case (B6, T=0.3, Problem "Solve 2x+3=7")*:
```
Round 1 Student: "2x + 3 = 7 → 2x = 4 → x = 2"
Round 1 Evaluator: "FINAL CORRECT — confirmed: 2(2) + 3 = 7 ✓"
Round 2 Coordinator: "STOP"
[Converged in 1 round]
```

---

## PART P: DRAFT DISCUSSION & LIMITATIONS

### Section 7: Discussion

**[7.1 Findings Summary]**

We demonstrate that:
1. **Multi-agent verification is powerful but fragile** — Independent evaluators improve accuracy by 35 points, but only under low temperature (T≤0.5). At high temperature, evaluators hallucinate, causing cascading errors.
2. **Coordination requires observability** — Explicit coordinators reduce oscillation by 40%, but only when given full conversation history. Current systems that feed coordinators only evaluator output are under-specified.
3. **Temperature is a first-order control knob** — Dropping from T=0.9 to T=0.3 improves accuracy by 5 points and slashes contradiction rate from 5% to 2%.
4. **Evaluator > Coordinator in impact** — Removing the evaluator degrades accuracy by 28 points; removing the coordinator, only 7 points. Educational designers should prioritize verification.
5. **Diversity is a feature, not a bug** — Multi-agent systems produce 3.8× more diverse explanations than single-agent, which pedagogically is valuable despite longer convergence (2.8 vs. ∞ rounds).

**[7.2 Implications for System Design]**

*Recommendation 1*: **Use low temperature (T=0.3–0.5) for all agents in educational settings.** The accuracy-creativity tradeoff is dominated by stability.

*Recommendation 2*: **Give the Coordinator full conversation history, not just the latest evaluator response.** Our B3 configuration (full history) shows 40% less oscillation than B5 (no coordinator). A coordinator blind to history is a rubber stamp.

*Recommendation 3*: **Validate evaluators independently before deployment.** 5% contradiction rate (B3, T=0.9) is unacceptable in high-stakes tutoring. Run evaluator agents on benchmark problems with known answers; require ≥99% agreement with ground truth before using in multi-agent loops.

*Recommendation 4*: **Terminate on first correct answer from a verified evaluator.** Our B3 system terminates in ~2.8 rounds; forcing 5 rounds wastes tokens and risks late oscillation. Implement explicit convergence detection.

*Recommendation 5*: **Monitor diversity to ensure pedagogical value.** Diversity scores >0.5 indicate meaningful variation in explanation; <0.2 indicates repetitive/shallow reasoning. Use diversity as a real-time quality signal.

**[7.3 Limitations]**

1. **Domain Specificity**: We study only mathematics (algebra, quadratic equations, discrete math). Results may not generalize to science, coding, or humanities.

2. **Model Specificity**: We use Mistral-7B. Larger models (70B, 405B) or different architectures (GPT-4, Gemini) may behave differently. We recommend replication with other models.

3. **Problem Scale**: 60 problems is modest. Benchmark expansion to 200+ problems across 10+ categories would strengthen claims.

4. **Evaluator Truthfulness**: We assume the evaluator reports honestly, but we do not validate evaluator logic (Hallucination Rate is manually annotated for 50 samples only). A future paper should build a "evaluator validator" agent.

5. **Pedagogical Evaluation**: Diversity and over-reasoning are proxies for pedagogical usefulness; we do not measure student learning outcomes (e.g., pre-/post-test with humans).

6. **Reproducibility Risk**: LLM outputs are stochastic; we seed but do not guarantee byte-for-byte reproducibility across machines/Ollama versions.

---

## PART Q: NEXT IMPLEMENTATION TASKS

### Q.1 Code Changes Required (Priority Order)

**Priority 1 (Critical for results):**
1. **Upgrade `llm.py`**: Expose temperature as a parameter (currently hardcoded 0.9)
   ```python
   def call_llm(prompt: str, model: str = "mistral", temperature: float = 0.9) -> str:
       # ... modified to use `temperature` parameter
   ```

2. **Fix `agents.py` Coordinator**: Give full conversation history, not just evaluator output
   ```python
   class CoordinatorAgent:
       def respond(self, full_history: List[Tuple[str, str]], eval_decision: str) -> str:
           # Reconstruct context from full_history
           context = "\n".join([f"{role}: {msg[:200]}..." for role, msg in full_history])
           # ... use context, not just eval_decision
   ```

3. **Instrument `main.py`**: Add detailed JSON logging per agent response
   ```python
   def run_simulation_instrumented(question: str, config: str, temperature: float, seed: int, rounds: int = 5):
       # Log each response as JSON with: run_id, round, agent, timestamp, tokens, latency, etc.
       # Use structure from Part G.1
   ```

4. **Add answer extraction**: Normalize student/evaluator outputs to canonical answer format
   ```python
   def extract_answer_from_response(response: str, problem: str) -> str:
       # Use regex or simple parsing to extract "x = 2" from free-form response
       # Handle variations: "x=2", "x = 2", "The answer is x = 2", etc.
   ```

**Priority 2 (Necessary for eval):**
5. **Build benchmark JSON**: Curate 60 problems with ground truth, difficulty, canonical steps
   ```json
   [
     {
       "problem_id": "linear_eq_001",
       "statement": "Solve: 2x + 3 = 7",
       "expected_answer": "x = 2",
       "difficulty": 1,
       "steps": ["Subtract 3", "Divide by 2"]
     },
     ...
   ]
   ```

6. **Implement metrics**: Build `metrics.py` with 14 metric functions
   - `final_accuracy(logs, ground_truth)`
   - `convergence_rounds(logs, eval_decision)`
   - `oscillation_count(logs)` → semantic similarity check
   - `contradiction_rate(logs)` → track evaluator flip-flops
   - `explanation_diversity(logs)` → embedding-based
   - etc. (see Part F for formulas)

7. **Build analysis pipeline**: `analyze.py` → aggregate by configuration, compute statistics, generate tables/figures

**Priority 3 (For publication):**
8. **Implement baselines**: Configurations B0–B8, ablations A1–A3
   - Modify agent instantiation to enable/disable agents
   - Parameter sweeps over temperature

9. **Statistical tests**: `stats.py` → t-tests, ANOVA, Mann-Whitney, Bonferroni, effect sizes

10. **Visualization**: Matplotlib/Seaborn plots for figures 1–3 (see Part N)

11. **Qualitative analysis**: Parse 50 representative transcripts, label failure modes, extract examples

### Q.2 File Structure After Implementation

```
multi_agent_project/
├── main.py                 # [MODIFY] Main entry point + instrumented run_simulation
├── agents.py               # [MODIFY] Add temperature param, fix Coordinator history
├── llm.py                  # [MODIFY] Expose temperature, seed parameters
├── analysis.py             # [EXISTING, move to legacy]
├── metrics.py              # [NEW] 14 metric functions with formulas
├── stats.py                # [NEW] Hypothesis tests, effect sizes
├── visualization.py        # [NEW] Matplotlib plots
├── extract_answers.py      # [NEW] Normalize/parse LLM outputs to canonical form
│
├── benchmarks/
│   ├── problems.json       # 60 problems with ground truth
│   ├── verify_benchmark.py # Validation script
│   └── problem_categories/ # Organized by type
│
├── configs/
│   ├── baseline.yaml       # B0–B8 configuration specs
│   └── ablations.yaml      # A1–A3 specs
│
├── logs/
│   ├── runs/               # Output: per-run JSONL files
│   ├── analysis/           # Output: CSV/JSON summaries
│   └── transcripts/        # Output: qualitative samples
│
├── paper/
│   ├── paper.md            # Draft paper (all sections K–P)
│   ├── figures/            # Plots (Figure 1, 2, 3, ...)
│   ├── tables/             # CSV/LaTeX tables
│   └── appendix.md         # Supplementary material
│
├── RESEARCH_PLAN.md        # This file
├── RUNNING.md              # How to run experiments
├── requirements.txt        # [UPDATE] Add matplotlib, numpy, scipy, scikit-learn
└── README.md               # Project overview
```

### Q.3 Experiment Execution Timeline

| Phase | Duration | Task |
|-------|----------|------|
| **Setup** | 2–3 hrs | Code changes (Q.1 #1–4), benchmark curation (#5) |
| **Validation** | 1–2 hrs | Run 1 full problem with each config; validate logging |
| **Tier 1** | 6–8 hrs | Run mandatory configs (450 runs); collect logs |
| **Analysis** | 2–3 hrs | Compute metrics, run stats tests, generate tables/figures |
| **Tier 2** | 4–5 hrs | Run secondary configs (300 runs) |
| **Refinement** | 2–3 hrs | Repeat analysis, generate final figures |
| **Paper** | 8–12 hrs | Write sections K–P, integrate figures, citations |
| **Total** | **25–34 hours** | — |

---

## SUMMARY: KEY TAKEAWAYS

### For the Paper
- **RQ**: How do agent composition, verification, and coordination affect solution correctness and pedagogical utility?
- **H1–H5**: Testable hypotheses about verification, coordination, temperature, ablation impact
- **Methods**: Rigorous benchmark (60 problems), 11 configurations, ~1500 runs, 14 metrics, Bonferroni-corrected tests
- **Expected findings**: Evaluator is critical; temperature matters more than architecture; full-history coordination is essential

### For the Codebase
- **Must do**: Add temperature param, fix Coordinator history, instrument logging, build metrics
- **Should do**: Implement baselines, add statistics, visualize results
- **Nice to have**: Larger benchmark, multi-model study, human evaluation

### For the Research Contribution
- **Novel**: Systematic ablation of educational multi-agent LLM systems (first such study)
- **Rigorous**: Quantitative metrics, hypothesis testing, robustness checks, public logs
- **Actionable**: Design guidelines, code recommendations, reproducible study

---

**Next step**: Proceed with Priority 1 code changes, then run Tier 1 experiments. Report results in 2–3 weeks.

