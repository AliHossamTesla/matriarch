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
| `query` | query **one** data source with filters on its properties; open only the rows you need. See *Queries and plans* below |
| `create_row` | create a page in the data source with the properties; the body is page content |
| `update_row` | update the page's properties; never rewrite another session's text |
| `child_page` | create a page whose parent is the row's page |
| `edit_page` | fetch the page, replace only the target section, write it back; re-fetch right before writing |

## Queries and plans

What the Notion tools allow depends on the workspace plan:

- **Filter queries** on one data source work on every plan. Use them by default.
- **SQL on one data source** works on every plan, but below the Business plan
  each SQL query counts against a limit shared by the whole workspace. Use SQL
  only when a filter cannot ask the question (for example a count or a group).
- **SQL across two or more data sources** needs the Business plan or higher.
  Below it the call fails with `This tool requires a Business plan or higher`
  (`entitlement_required`). Never rely on it: query each data source on its own
  and join the results in the session.

If a query fails with `entitlement_required`, do not retry it. Run the same
question as one filter query per data source and go on.

## Notes

- Addresses are page URLs and `collection://` data source URLs; the registry
  row's `Data sources` stores them.
- Notion has no locks. Follow the claim check and own-rows rules in
  `../memory.md` §4.
- Very long text: split into child pages and link them.
