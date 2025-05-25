# UpperNet

UpperNet is a hierarchical agent network.<br>
It is a PoC for an LLM capable of executing complex tasks 
until they're complete without being limited by context length, 
or by hallucinations.

## Theory

To be written.

## Implementation (brief)

### Agent types

- **Manager** - a tree node, splits complex/abstract tasks into simpler ones.
- **Worker** - a tree leaf, executes the most technical task fragments.
- **Overseer** - an out-of-tree agent managing creation of new agents.
- **Verifier** - an out-of-tree agent mediating in submission of **Worker's** work.

### Agent relations

To be written.

### Agent tooling

To be written.

## Implementation (detailed)

To be written.