# Public-source research and individuals

ENVY can search the public web, discover indexed CourtListener/RECAP records, read accessible pages and PDFs, and search documents you explicitly add. It cannot obtain “everything” about a person, bypass access controls, or determine truth from a confident answer alone.

## Research a person

```text
/person Alex Example, fictional Project Juniper coordinator
```

For real research, provide a name plus relevant context such as professional role, organization, court, approximate year, or jurisdiction. A common name alone is insufficient. The assistant should ask for clarification when it cannot distinguish namesakes.

Use a focused request:

> Research the public professional history and published work of [name], [organization]. Confirm identity across sources. Separate documented facts from allegations and disputed claims. Link each material assertion to evidence and dates. State what could not be verified.

For records:

> Find public filings relevant to [name], [court/jurisdiction], [approximate year]. Verify parties and case number before linking a record to this person. Distinguish allegations from judicial findings. Include outcomes and appeals where available, with dates and PDF pages.

This is a research workflow, not a private-person dossier builder. Do not collect credentials, government identifiers, home addresses, private contact details, family-member dossiers, or real-time whereabouts. Public availability does not make irrelevant personal information useful evidence. The bundled example person, dates, and document are fictional.

## Evidence workflow

1. Establish identity and the question being investigated.
2. Search for primary documents and relevant reporting.
3. Open sources; snippets are only leads.
4. Record exact short quotations and page references for important claims.
5. Search for conflicting sources, later orders, corrections, or updated dates.
6. Label each claim: documented, alleged, inferred, disputed, or unverified.
7. Preserve what is missing. No result is not evidence of no record.

`/check <claim>` asks the model for an evidence table. `/audit` checks source IDs and flags search-snippet-only citations. Neither replaces comparing each claim with the underlying document. OCR can alter words or numbers; inspect the original before quoting a scan.

## Local documents

```text
/library-add examples/project-juniper.txt
/offline
/library-find proposed launch date
/check The Project Juniper launch definitely happened on 12 November 2030
```

The fictional fixture contains an outdated draft date and a revised proposed date. A correct answer must distinguish a proposed schedule from an event that actually occurred. The model can use the library offline. Keyword search is not exhaustive semantic search; try alternate terms and page ranges.

## CourtListener and PACER

`/court` searches free public indexes. If you have a CourtListener API token, `/account-add courtlistener` stores it in Keychain and `/account-use courtlistener` activates it for the session. Only selected read-only record endpoints are implemented; API access and rate limits still apply. See [CourtListener documentation](https://www.courtlistener.com/help/api/rest/).

Some docket webpages reject automated requests even when search results or linked PDFs are accessible. Read a publicly downloadable filing when possible; otherwise report the access failure. No bypass is implemented.

`/pacer` opens the official site for manual use. Download a record there, then use `/file` or `/library-add`. This project does not send stored PACER passwords to a model, authenticate automatically, submit paid searches, or purchase documents. See [PACER pricing](https://pacer.uscourts.gov/pacer-pricing-how-fees-work); do not assume free model inference makes court access free.
