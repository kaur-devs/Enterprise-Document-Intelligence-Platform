# UI/UX Wireframes — KnowledgeHub AI

Low-fidelity layout reference for the four main views. All four share a fixed left sidebar (nav + live system status) and a scrollable main content area.

## Shared shell

```
┌──────────────┬──────────────────────────────────────────────┐
│ ● Brand       │  <view title>                                │
│              │  <view description>                           │
│ ▸ Dashboard   │                                                │
│   Knowledge   │  ...view content...                           │
│   Chat        │                                                │
│   Search      │                                                │
│              │                                                │
│              │                                                │
│ ┌──────────┐ │                                                │
│ │ Database ●│ │                                                │
│ │ Vectors  ●│ │                                                │
│ │ Gemini   ●│ │                                                │
│ └──────────┘ │                                                │
└──────────────┴──────────────────────────────────────────────┘
```

## Dashboard (default landing view)

```
┌───────────┬───────────────┬───────────────┐
│ Documents │ Chunks/Embeds │ Storage Used  │
│    12     │      143      │    4.2 MB     │
└───────────┴───────────────┴───────────────┘
┌─────────────────────────────────────────────┐
│ Recent Chats                                 │
│ Question              Grounded   Time        │
│ ────────────────────────────────────────────│
│ What is the budget?      Yes    2m ago       │
│ Capital of Japan?        No     5m ago       │
└─────────────────────────────────────────────┘
```

## Knowledge Base

```
┌─────────────────────────────────────────────┐
│           ⬆  drag/drop or click to upload    │
└─────────────────────────────────────────────┘
┌─────────────────────────────────────────────┐
│ Name      Type  Size   Chunks Status    ⟲ 🗑 │
│ ──────────────────────────────────────────── │
│ doc.pdf   pdf   1.2MB    18   [indexed]  ⟲ 🗑 │
└─────────────────────────────────────────────┘

Duplicate → modal: "Upload anyway?" [Cancel] [Upload anyway]
Delete    → modal: "Delete this document?" [Cancel] [Delete]
```

## Chat

```
┌───────────────────────────────┬───────────────┐
│  [user] What is the budget?   │ Search scope   │
│                                │ ☑ All docs     │
│  [bot] 42M euros.              │ ☐ doc.pdf      │
│  ┌ doc.pdf · p.1 ┐             │                │
│                                │                │
│  [user] Capital of Japan?      │                │
│  [bot] Couldn't find relevant  │                │
│  ⚠ Not grounded in your docs   │                │
├───────────────────────────────┤                │
│ [ Ask a question... ] [Send]   │                │
└───────────────────────────────┴───────────────┘
```

## Search

```
┌───────────────────────────────┬───────────────┐
│ [ Search your documents... ] 🔍│ Search scope   │
│                                │ ☑ All docs     │
│ ┌───────────────────────────┐  │ ☐ doc.pdf      │
│ │ doc.pdf · p.1      69.5%  │  │                │
│ │ "...matched chunk text..."│  │                │
│ └───────────────────────────┘  │                │
└───────────────────────────────┴───────────────┘
```

These reflect the actual built layout (see [frontend/src/components](../frontend/src/components)) — documented after the fact as a design reference rather than a pre-build spec, since the shared CSS design system (`frontend/src/index.css`) was already in place before this feature work started.
