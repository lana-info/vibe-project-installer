# Frontend Design Direction

Use this file before building visible UI. The goal is not to install many design systems; the goal is to make a small set of polished components and tune them carefully.

## Web

Default approach: start from shadcn/ui-style components, then tune each component for this product's visual identity.

- Use the existing component system before adding another UI library.
- Build the real workflow screen first, not a marketing placeholder.
- Polish important components in 2-3 passes: layout, states, spacing, visual tone.
- Keep components simple enough that Codex can safely edit them.
- Prefer consistent tokens and component variants over one-off styling.

## Mobile

Default approach: before feature development, ask the agent to create a small mobile component library for this project.

Do not add Tamagui by default. Use it only if the project has a clear reason and accepts the extra setup cost.

The starter mobile library should cover:

- screen layout;
- buttons;
- inputs;
- cards;
- list rows;
- empty/loading/error states;
- tabs/navigation surfaces;
- modal/sheet patterns;
- typography;
- theme colors and spacing.

## Design Taste

Use references like 21st.dev for taste, but do not copy blindly. Work carefully and tune details: spacing, hierarchy, contrast, states, and motion.

## Prompt

```text
Before implementing this screen, inspect the existing UI components and design tokens.
Do not add a new UI library.
Propose the smallest component set needed for this workflow.
Then implement the screen in 2-3 quality passes: structure, visual polish, responsive states.
```

