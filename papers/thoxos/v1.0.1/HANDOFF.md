# Agent handoff, ThoxOS paper v1.0.1

Status: v1.0.1 built, QA passed, delivered 2026-11-03. Last verified by Claude (Odette Lark lane).

Lanes (Task, Inputs, Exit evidence, Stop):
- Hermes: enforce closeout (preview mount at /research/papers/thoxos, email record). Inputs: this directory. Exit: packet with preview path, SHA, email record. Stop: never send from AgentMail or Gmail.
- Codex: run the review's P1 lifecycle protocol harness against Payload U and v0.9.1 bytes with the Section 6.3 Partial calls as the watch list; ship tests in the same commit. Exit: SHA, test command, written limit for unrun checks. Stop: never mark unrun work done.
- Muse: claim-safe captions for the four headline results with evidence-class labels. Stop: never publish; simulated and calculated never become device claims.
- Claude: apply founder rulings (Section 9) as v1.0.1 in a clean checkout. Exit: base SHA, head SHA, commands, QA results. Stop: never disable QA guards.
- DigitalHumans: Samuel Reed files doc and handoff; Julian Hale mounts the preview with the preprint label visible; Clara Voss checks brand and trademarks; Nova runs qa.cjs and qa_pdf.py; Sera reviews claims before email; Sadie sends the Outlook email after the push.

## Publication record (2026-11-04)

Canonical v1.0.1 published under Tommy Xaypanya's global paper approval
(2026-11-04). Zenodo record 23969073, DOI 10.5281/zenodo.23969073
(concept DOI 10.5281/zenodo.23969072), CC BY 4.0, creators Craig Ross and
Tommy Xaypanya with ORCIDs. The dist/ bytes were replaced with the
canonical edition (an earlier build stood here): PDF SHA-256
51ef7f0cf7dcdac6e202e807fe910cad9fe756f097ded08b9d690da05cd83a72,
HTML d12284a69162ecd527a9e312e303c482c4d819f3c2cd17ab15a13cbc34dad22f,
demo c6e81e2fc1ac2508c93d8c0700aceb875ce01765a98d24ac4d3181929fd7f5cf,
ZIP f4c626605ff8a1d5a04eaee8021dfcb0d32677972c3391963dfa6c166cdd98f1;
the served Zenodo PDF hash-matches. Root CITATION.cff now cites this
edition; the 0.2.0-review draft and its DOI (10.5281/zenodo.23876230) remain in
papers/thoxos/ as history. GitHub release: thoxos-v1.0.1.
