# Security boundaries and maintenance record

Author/developer Matthew X Murphy, https://MatthewxMurphy.com.
Product attribution: https://builtnotbegged.com. Preserve actual existing project
licenses, upstream copyright and release ownership. No new license is granted
where existing first-party distribution terms remain unassigned.

## Scope

Source fixes for APP-06, October16,2026. No deployment, provider action, artifact
publication or software-version bump. User's model selection does not change
software versions; historical releases and API compatibility remain intact.

## Behavior and configuration

Queue adapters execute a fixed absolute executable with shell=False. The execution prefix is fixed before any data is admitted. Python/Node require a fixed absolute script with no interpreter switches. Only --slug={slug}, --owner={owner}, and --body-file={comment_file} (or --comment-file) are accepted; space-separated template values are normalized to single --key=value arguments. Unknown switches, dynamic program/script/option positions, positional arguments and raw comment substitutions fail closed. Comment text travels only through a private temporary file, which is cleaned up. Adapter owners must parse the named data fields without evaluating their contents. A local nonblocking lock covers generation/processing; queue updates use atomic0600 files. Each attempt is persisted before execution; interrupted/failed/unconfirmed outcomes become uncertain and are never auto-retried. The per-run cap counts attempts, including failures. Corrupt durable state fails closed, and regeneration retains frozen attempts/receipts outside the current selection.

Posting remains disabled by default. Existing postCommandTemplate configuration must name an absolute owned adapter, for example /usr/local/bin/owned-post-adapter --slug "{slug}" --body-file "{comment_file}". Legacy templates using raw comment_text/comment_text_b64, positional fields, interpreter flags or custom switches must migrate to this closed protocol before posting resumes. A Python example is `/absolute/python3 /absolute/adapter.py --slug "{slug}" --owner "{owner}" --body-file "{comment_file}"`. The adapter must independently reconcile platform delivery and emit JSON with confirmed:true and a nonempty receipt_id. Nonzero exit, timeout or malformed/unconfirmed output is uncertain. An owner must inspect native delivery before deliberately requeuing; a process exit alone is not delivery proof. This is a single-host POSIX-lock queue, not a distributed or multi-tenant service.

### Unique delivery identities — October 18, 2026

Repeated source findings with the same stable queue ID are selected once, before
the unique-item limit is applied. Generation and delivery validate every durable
record before changing state or invoking any adapter: IDs must be nonempty strings
and must be unique across queued, in-flight, uncertain and posted records. A bad
record anywhere holds the whole queue, including earlier otherwise valid items.

Historical queues containing duplicate IDs now stop for owner reconciliation.
Keep the original queue and native delivery evidence; inspect all conflicting
attempts and receipts before preparing a corrected queue. Do not delete a posted
or uncertain record merely to resume automatic posting. The worker preserves the
malformed file bytes rather than merging conflicting receipts or falling back to
an older in-memory queue. This prevents duplicate local claims; provider-side
idempotency and actual delivery reconciliation remain the owned adapter's duty.

The isolated regression includes repeated input findings, durable duplicates in
each delivery state, and invalid IDs after a valid first row. Denied cases invoke
no adapter and preserve queue bytes. The existing literal-argument, interrupted
claim, uncertain outcome and concurrent-owner contracts remain required.

## Test and rollback

Required local security check: `python3 -m unittest discover -s tests -v`. Tests use synthetic temporary state,
mock adapters or local HTTP/Fastify fixtures; they never contact provider services
or establish native delivery. Syntax/build and rendered checks are recorded in
the private source receipt. Revert this reviewed code commit for a source rollback;
retain new private state and authorization configuration. Do not restore anonymous
network access or old public databases as a routine rollback.

## Engineering SOP adoption and remaining gaps

Read https://github.com/matthewxmurphy/developer-standards and the project's own
instructions before maintenance. This scoped change adds security contracts,
regression tests and operational notes. Exact staged/index bytes are scanned and
manually reviewed before commit. Existing licenses/upstream notices are retained;
missing distribution choices await the owner's decision.

This document is not a claim of complete engineering adoption: portable checker
integration/engineering.json, full architecture/API/contribution/support docs,
required remote checks/branch enforcement and release/runtime acceptance remain
to be assessed in their own scoped maintenance work. The portable helper currently
has internal distribution terms; public products must not copy it without recorded
permission. A source commit and offline test pass do not certify a release.

### Claim durability and receipt validation — October 18, 2026

Atomic queue replacement synchronizes the private temporary file, replaces the queue path and synchronizes the parent directory before returning. A failed/unsupported directory sync aborts the run before an adapter can use that claim. The visible interrupted claim remains held for owner reconciliation; it is not automatically retried. Local tests verify file-sync/directory-sync/adapter ordering and injected directory-sync failure on this operating system. They do not establish hardware power-loss recovery or filesystem/controller guarantees.

Adapter receipt IDs must contain a non-whitespace character and remain within the existing 200-character bound. Usable IDs retain their exact original bytes; blank/whitespace-only confirmations are uncertain and cannot trigger automatic retry. Native delivery remains the owned adapter's responsibility.
