# Backend: notion

The default for both memories. Works in every tool that has the Notion
connector or MCP server (`../memory.md` §6).

## Layout

- **Central:** a registry database (`memory.central.registry`, default
  `Matriarch · Projects`); per project a hub page `<Project>'s Handoff` with the
  five databases under it.
- **Personal:** a private page (default title `Matriarch · Personal`) with one
  database `Personal` (schema in `../memory.md` §2). Only its owner has access.
  `setup` creates it and writes its URL to `memory.personal.url`; sessions open
  it **by that URL only**, never by a title search, which could find a
  teammate's page.

## Operations

| Operation | How |
| --- | --- |
| `find_registry` | search for a database with that exact title; if several, ask the owner |
| `read_page` | fetch the page by URL or ID |
| `schema` | fetch the data source (`collection://…`) once per session; use its exact property names and select options |
| `query` | query the data source with filters on properties (or SQL where the plan allows it); open only the rows you need |
| `create_row` | create a page in the data source with the properties; the body is page content |
| `update_row` | update the page's properties; never rewrite another session's text |
| `child_page` | create a page whose parent is the row's page |
| `edit_page` | fetch the page, replace only the target section, write it back; re-fetch right before writing |

## Notes

- Addresses are page URLs and `collection://` data source URLs; the registry
  row's `Data sources` stores them.
- Notion has no locks. Follow the claim check and own-rows rules in
  `../memory.md` §4.
- Very long text: split into child pages and link them.
