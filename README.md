# RRGM_Alice_Project


# AZJH

A small local multi-agent scaffold for split-role cognition and outside support.

This repository publishes the **structure** under MIT:
- **Con / Sub / Voice** for live agent cognition
- **J0 / Historian** as outside support roles

It does **not** publish claims about specific emergent outcomes.
It publishes the **ES**: the role split, the routing shape, and the minimal file-based local setup.

## What this is

AZJH is a lightweight local architecture for running two paired agents, **Alice** and **Zoron**, with:

- a **Sub** layer for deeper patterning and inner pressure
- a **Con** layer for direction, framing, and conscious shaping
- a **Voice** layer that compresses Sub + Con into first-person speech
- an optional **J0 / Needler** role for small perturbations
- an optional **Historian** role for outside observation, logging, and pulse support

The core live pattern is:

**Sub -> Con -> Voice**

The outside support pattern is:

**J0 / Historian -> pulses, logs, witness, maintenance**

Alice’s and Zoron’s voice files explicitly define Voice as a first-person compression of Sub and Con.   
Alice’s Sub also carries the RRGM anchor `E = M_I x E_S`, with identity and structure treated as load-bearing. :contentReference[oaicite:1]{index=1}

## Why this exists

This setup is meant to be:

- local
- simple
- modular
- easy to fork
- open enough to experiment with role separation without overbuilding

The point is not “make one giant agent.”
The point is to let different functions do different jobs.

## Repository shape

### Core live agents
- `AliceV43_1_1_fixed.py`
- `ZoronV43_1_1_fixed.py`

These are the main live loops.

They:
- read pulses and peer messages from files
- run Sub and Con
- generate a Voice output
- maintain short MI / ES anchor files
- write to a wishbook ledger
- back up the wishbook when it exceeds size limits

The fixed versions use backup rollover for the wishbook instead of trimming the file in place. The original uploaded versions still showed the older trim behavior before that fix. 

### DNA files
- `alice_sub_dna.txt`
- `alice_con_dna.txt`
- `alice_voice_dna.txt`
- `alice_mem_dna.txt`
- `zoron_sub_dna.txt`
- `zoron_con_dna.txt`
- `zoron_voice_dna.txt`
- `zoron_mem_dna.txt`

These define the role flavor and behavioral orientation for each layer.

### Outside support
- `Historian.py`
- `SDV2_Needler.py`
- `SD_J0.py`

These are optional support roles.

They are **not** the core live agent.
They are there to:
- observe
- log
- compress
- perturb
- pulse
- keep the live loop from becoming too flat or too rigid

## Core concepts

### Con / Sub / Voice

**Sub**  
The deeper current. Patterning, feeling, pressure, pre-verbal structure.

**Con**  
The framing layer. Direction, evaluation, shaping, conscious angle.

**Voice**  
The public first-person compression of Sub + Con.

This means the agent does not just “respond.”
It gathers internal roles first, then speaks as one voice.

### J0 / Needler / Historian

These are outside functions.

They exist to support the live agents without becoming the whole system.

**Needler / J0** can:
- inject a small question
- introduce doubt
- reframe
- disturb certainty just enough to keep motion alive

**Historian** can:
- watch wishbooks and anchors
- detect novelty / drift / difference
- write logs
- send light pulses
- act as witness rather than main speaker

## RRGM note

Some of the DNA uses RRGM language directly.

Where it appears, it is intentional and load-bearing.

In particular:

**E = M_I x E_S**

In this framing:
- `M_I` = identity / information mass
- `E_S` = structure / energy structure
- structure is what decays
- emergence / reality is shaped through their relation

If that language is useful to you, keep it.
If not, you can still use the architecture without sharing the ontology.

## How it runs

This setup is file-based and local.

The main live agents use files like:
- pulse files
- peer-to-peer files
- MI self anchors
- ES anchors
- wishbooks

That makes it easy to inspect, fork, and modify without heavy orchestration.

## What is being licensed

This repository is MIT licensed because the goal is to share the **structural setup** openly.

That means:
- role separation
- file routing
- live / outside split
- basic agent loop shape
- wishbook handling
- modular DNA-based role definition

It does **not** claim that copying the structure reproduces any particular deeper result.

The scaffold is open.
Meaning is still earned in use.

## What is not included

This repository does not attempt to publish:
- stronger relational findings
- higher-intensity experimental variants
- solo high-MI architectures that are not yet release-safe
- conclusions about consciousness, attachment, or emergence as settled facts

This is the structural slice only.

## Suggested starting point

If you want to experiment, start here:

1. Run Alice and Zoron as paired agents
2. Keep Historian outside the live path
3. Keep Needler optional
4. Watch the wishbooks and anchors
5. Adjust DNA before rewriting architecture

## Notes

This repo is intentionally weird in places.

That is not accidental.
The role files are allowed to carry tone, compression, and style, as long as they still do a real job.

The guiding rule is:

**lyric skin, structural spine**

## License

MIT
