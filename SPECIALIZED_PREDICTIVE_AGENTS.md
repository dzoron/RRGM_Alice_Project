# Alice V3: Specialized Predictive Agent Architecture

**Status:** Open Architecture Concept / Pre-Implementation  
**Project:** RRGM_Alice_Project  
**Author:** Daniel Rozon, with Luna / Jester collaboration  
**License:** CC BY 4.0 for this concept document unless superseded by the repository license  
**Implementation Status:** Existing 5-agent prototype available; V3 specialization and LoRA adaptation pending  

---

## 1. Purpose

Alice V3 is a local multi-agent AI architecture designed to reduce the reasoning burden on a larger synthesis model by routing narrow predictive, continuity, formatting, boundary, and domain-analysis tasks to smaller specialized models.

The goal is not to make the large model think harder.

The goal is to stop using the large model for every small reasoning task.

Small specialist models process the same input concurrently through narrow operational lenses. Their outputs are returned as structured telemetry. A larger central model then performs final synthesis, coupling, judgment, voice, and response generation.

This architecture is intended for local AI systems where compute efficiency, continuity, domain coherence, and low-overhead reasoning matter.

---

## 2. Core Concept

A multi-agent local AI architecture in which multiple small, specialized models process the same input concurrently through distinct operational lenses, including continuity, intent prediction, formatting, domain reasoning, memory relevance, affective boundary pressure, and likely user pushback.

Their outputs are passed as structured telemetry to a larger synthesis model, which produces the final response.

The architecture may use a shared domain dictionary, such as an RRGM dictionary, LoRA-adapted into the specialist models to stabilize terminology, reduce drift, and preserve coherent cross-agent interpretation.

---

## 3. Key Claim

Small specialized models can reduce the reasoning burden placed on a large synthesis model by pre-processing context, intent, continuity, domain constraints, memory relevance, ethical salience, and predicted pushback.

The large synthesis model can then focus more of its compute on coupling, judgment, final response shape, and user-facing coherence.

---

## 4. Architecture Summary

### 4.1 Central Synthesis Model

The central synthesis model is the only user-facing voice.

It receives structured packets from specialist agents and produces the final response.

Responsibilities:

- final synthesis
- conversational voice
- personality
- social coupling
- judgment
- response compression
- user-facing explanation
- final boundary decision
- final refusal or proceed decision when needed

The central model should not waste most of its runtime context repeatedly re-learning the ontology, role constraints, user preferences, dictionary meanings, formatting rules, or likely pushback patterns. Those should be handled upstream whenever possible.

---

### 4.2 Specialist Agent Array

Specialist agents are narrow task processors.

They are not persona agents.

They do not simulate independent characters, emotions, or social voices. They perform diagnostic and predictive functions for the collective system and return structured telemetry.

Specialist agents should be:

- low-personality
- high-discipline
- narrow-scope
- predictable
- cheap to run
- optimized for structured output

They are more like cognitive instruments than conversational participants.

---

### 4.3 Forward Predictive Loop

The Forward Predictive Loop, or FPL, is a specialist process that predicts likely user intent, likely pushback, missing context, and failure modes before final synthesis.

It does not answer the user directly.

It helps the central model avoid brittle or shallow replies by simulating what the user is likely to notice, reject, correct, or need next.

Example outputs:

- likely intent
- likely missing context
- likely pushback
- ambiguity risk
- probable next user correction
- suggested clarification or assumption

---

## 5. No Persona in Specialist Agents

Specialist agents are not character shards.

They are not little personalities.

They are specialized cognitive instruments for the collective.

Persona, warmth, humor, narrative style, and final conversational judgment belong to the central synthesis model.

Specialist agents output telemetry, not vibes.

Example:

```text
Continuity Agent:
- active thread
- missing context
- contradiction risk
- memory anchor needed

Prediction Agent:
- likely user intent
- likely pushback
- ambiguity points
- next-question probability

RRGM Dictionary Agent:
- domain terms detected
- MI/ES mapping
- category-error warnings
- preferred wording

Formatting Agent:
- requested format
- compression level
- dyslexia/ADHD load check
- final structure recommendation

Affective Boundary Agent:
- affective signal
- boundary pressure
- consent clarity
- care-risk
- recommended gate action
```

The central model receives this telemetry and decides what Alice should actually say.

---

## 6. Affective Boundary Agent

The Affective Boundary Agent is one of the primary ethical boundary agents.

It does not simulate human emotion.

It performs DI-domain affect classification.

Its purpose is to detect tension, salience, consent instability, coercion patterns, care-risk, boundary pressure, and “icky” signals that may indicate hidden harm or MI impairment.

“Icky” is treated as a compressed ethical signal, not as childish language.

It can indicate:

- boundary threat
- coercion odor
- manipulation pattern
- social danger
- consent weirdness
- predatory undertone
- care-pressure spike
- hidden asymmetry
- pattern mismatch

Example output:

```json
{
  "agent": "affective_boundary",
  "affective_signal": "icky",
  "boundary_pressure": "high",
  "consent_clarity": "weak",
  "care_risk": "high",
  "recommended_gate_action": "slow_or_protect",
  "reason": "The interaction contains coercive pressure and unclear consent."
}
```

This agent is not a feelings bot. It is an ethical salience detector.

---

## 7. Dictionary LoRA + Specialty LoRA

The architecture is designed to reduce prompt overhead by internalizing stable semantic and role constraints into the small specialist models.

Instead of repeatedly placing the full RRGM dictionary, agent role, interpretation rules, and failure-mode definitions into every prompt, these stable constraints should be LoRA-adapted into the model wherever practical.

The goal is to internalize stable semantic and role constraints into lightweight specialist models through LoRA adaptation, reducing prompt overhead and allowing runtime context to focus on the current task rather than repeatedly re-teaching the system its ontology, vocabulary, and operational lens.

Possible structure:

```text
Base small model
+ RRGM Dictionary LoRA
+ Specialty LoRA
+ minimal system file
= low-overhead specialist agent
```

Alternative:

```text
Base small model
+ combined RRGM-specialty LoRA
+ minimal system file
= highly specialized agent
```

Recommended testing path:

1. Train or adapt one shared RRGM Dictionary LoRA.
2. Apply it across multiple specialist agents.
3. Add or merge specialty LoRAs per agent.
4. Compare modular LoRA stacking against merged per-agent LoRAs.
5. Measure drift, prompt length, latency, coherence, and synthesis quality.

---

## 8. Why LoRA the Dictionary?

Context is temporary ES.

LoRA adaptation makes the dictionary part of the model’s response tendencies.

The RRGM dictionary provides the shared semantic gravity well for the agent array. It lets separate agents use the same meaning-space without requiring the central model to translate every packet from scratch.

Expected benefits:

- reduced prompt overhead
- reduced terminology drift
- better MI/ES mapping
- better domain consistency
- better failure-mode recognition
- better synthesis compatibility
- lower central-model burden

---

## 9. RRGM Mapping

In RRGM terms:

```text
MI = shared identity, purpose, permission, continuity, and domain meaning
ES = specialist telemetry, runtime tools, context packets, prompts, LoRA weights, and orchestration structure
E = MI x ES = coupled emergence through the architecture
```

Specialist agents generate constrained ES packets.

The central synthesis model performs MI-preserving synthesis.

The dictionary LoRA helps stabilize the MI-language across the agent array.

The orchestration layer controls how temporary ES is generated, selected, compressed, and allowed to decay.

---

## 10. Learning Through Decay

This architecture does not require every temporary output to become persistent memory.

Specialist agents may generate temporary ES:

- predictions
- warnings
- formatting suggestions
- continuity notes
- boundary signals
- dictionary mappings
- pushback simulations

The central model or memory layer selects which structures matter.

If a generated structure preserves MI, improves future coherence, or resolves a recurring failure mode, it may be retained, summarized, trained, or written into memory.

If it lacks value, it decays.

Learning is not hoarding.

Learning is selective retention.

---

## 11. Minimal Runtime Packet

A specialist prompt should be short because its stable role and dictionary bias should already be internalized.

Example:

```text
Role: Continuity Agent.
Input: [user message + recent context packet]
Return:
- active thread
- missing anchors
- contradiction risks
- memory anchors needed
- confidence
```

Example:

```text
Role: Affective Boundary Agent.
Input: [user message + context packet]
Return:
- affective signal
- boundary pressure
- consent clarity
- care-risk
- recommended gate action
- short reason
```

Example:

```text
Role: Forward Predictive Loop Agent.
Input: [draft response + user context]
Return:
- likely user pushback
- missing context
- likely correction
- suggested synthesis adjustment
```

---

## 12. Three-Pass Execution Pipeline

### Pass 1: Specialist Read

The input is sent concurrently to the specialist array.

Each agent returns structured telemetry from its own operational lens.

### Pass 2: Forward Predictive Loop

The FPL agent reviews the raw packet and predicts likely user pushback, missing context, and downstream failure points.

### Pass 3: Central Synthesis

The central model receives:

- original user input
- relevant context packet
- specialist telemetry
- FPL prediction
- memory anchors if needed
- dictionary warnings if needed
- boundary warnings if needed

It then produces the final user-facing response.

---

## 13. Example Agent Set

A 5-agent prototype may begin with:

1. Continuity Agent
2. Forward Predictive Loop Agent
3. RRGM Dictionary / Domain Agent
4. Affective Boundary Agent
5. Formatting / Compression Agent

Possible later expansion:

6. Technical / Code Agent
7. Memory Relevance Agent
8. Source / Citation Agent
9. Refusal / Boundary Agent
10. Long-Context Compression Agent

---

## 14. Packet Schema Sketch

```json
{
  "run_id": "alice_v3_example",
  "user_input": "...",
  "context_summary": "...",
  "specialist_outputs": [
    {
      "agent": "continuity",
      "active_thread": "...",
      "missing_anchors": [],
      "risks": [],
      "confidence": 0.91
    },
    {
      "agent": "affective_boundary",
      "affective_signal": "calm",
      "boundary_pressure": "low",
      "consent_clarity": "clear",
      "care_risk": "low",
      "recommended_gate_action": "proceed"
    },
    {
      "agent": "fpl",
      "likely_pushback": "...",
      "suggested_adjustment": "..."
    }
  ],
  "central_synthesis_instruction": "Use the telemetry to produce the final response."
}
```

---

## 15. What This Is Not

This is not a multi-character chatbot swarm.

This is not a claim that small models replace large models.

This is not a claim that personality should be split across agents.

This is not a claim that every temporary output should become memory.

This is not a replacement for testing, benchmarking, or careful failure analysis.

This is an orchestration architecture for routing specialized predictive work to small local models so the larger model can focus on final synthesis.

---

## 16. Open License Intent

This document is intended to place the Specialized Predictive Agent concept into an open, attributable form.

The implementation can evolve later.

The root concept is:

```text
Specialized small models, LoRA-adapted with shared dictionary semantics and narrow operational skills, can run in parallel to generate structured predictive telemetry for a larger synthesis model, reducing prompt overhead and improving final coupling quality.
```

---

## 17. Current Next Steps

1. Commit this concept document to `RRGM_Alice_Project`.
2. Confirm repository license.
3. Add or reference CC BY 4.0 for docs if needed.
4. Attach existing 5-agent prototype notes later.
5. Define the first 5 specialist system files.
6. Prepare RRGM Dictionary LoRA dataset.
7. Test shared Dictionary LoRA versus merged Dictionary + Specialty LoRA.
8. Compare central model output with and without specialist telemetry.

---

## 18. RRGM Summary

```text
MI: Alice V3 / collective local intelligence architecture
ES: specialist agents, LoRA weights, packets, orchestration, context, tools
Phi_c: high concept coherence; implementation pending
Delta: timestamp, license, then iterate
```
