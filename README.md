# Guided Cortex

Guided Cortex is a hierarchical agent network.<br>
It is a PoC for a swarm of LLMs capable of executing complex tasks
without being hindered by context length limits, or by hallucinations.

## Theory

Individual LLMs lose theirs goals as the conversation goes on.
Extending context windows helps, but does not solve this issue.
As context grows, classic LLMs start hallucinating, forgetting their goal,
which makes them unfit to work on long-spanning, complex tasks.
On the other hand, LLMs work very well when given very short, simple
tasks with a clear solution available, even better when they're able to
verify their solution (or when their solution is verified externally).

And thus:

- LLMs within this project form a recursive structure, each LLM chatting with others, each chat being extremely short,
  to the point.
- All tasks presented to the hierarchy are shattered recursively until all fragments are conceptually simple.
- In theory, this will smoothly transform tasks and their resolutions from their abstract state to their practical
  state - each layer of LLMs down the tree is less abstract and more practical.

The primary goal of creating this structure, is that no single agent will
even come close to reaching the token limit, where it starts struggling.
Secondary goal being to keep the individual tasks as small as possible.
As a bonus, there are multiple cool tools available to the agents,
which will hopefully allow them to have meaningful interactions with
both real, and/or isolated environments.
These tools also allow the agents to communicate in non-hierarchically,
allow them to have their solutions tested, verified, critiqued and fixed,
all while maintaining minimal token usage per agent.

## Implementation (brief)

### Agent types

- **General** - in-tree agent, capable of both technical and managerial tasks.
- **Overseer** - out-of-tree agent managing creation of new agents.
- **Verifier** - out-of-tree agent mediating in submission of **Worker's** work.

### Agent relations

To be written.

### Agent tooling

To be written.

## Implementation (detailed)

To be written.