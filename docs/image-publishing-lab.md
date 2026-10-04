# Publish a tested image to GHCR

## Quick reference

First review and merge the image-publishing PR. Then update local main and confirm
its CI passes. The learner will create and push a fresh version tag on main:

```bash
git switch main
git pull --ff-only
git tag -a v0.1.0 -m "First tested container release"
git push origin v0.1.0
```

These are release instructions, not a request to run them before PR review.
Never reuse/move a published version tag. The initial container release number is
independent of the API's internal 0.2.0 version; align them in a future release if desired.

## Flow and vocabulary

Tag push -> checkout -> verify version/main ancestry -> build/test -> scan ->
GHCR login -> tag/push the SAME local image -> record digest and scan evidence.

Registry: stores images, not running applications. Image tag: readable name, technically
movable. Digest: content identity, used for exact deployment. Git tag: selects source
commit and triggers release; Docker tag: names the built image. They are different.

Addresses: ghcr.io/prashantkumbhare/trading-api:v0.1.0 and a sha-<full-source-commit>
tag. release.txt records the full registry digest reference. Pull by that reference
to retrieve exactly those bytes. This first build is linux/amd64 for our laptops.

The integration script removes test containers/volume but retains trading-api:ci.
The release job scans and pushes that image without rebuilding it. It scans the API
image with Grype 0.120.0, blocking fixable HIGH/CRITICAL findings. Unfixed findings
are outside this first gate; report success does not mean there are no vulnerabilities.
Scanner/database failures also stop publishing. Read the report and remediate instead
of weakening the gate. Scanning the PostgreSQL dependency is later work.

GitHub supplies a short-lived GITHUB_TOKEN with packages:write; no personal token is
needed for workflow publishing. Checkout avoids saving credentials. The image source
label links it to this repository. Packages normally start private even when the
source repository is public; inspect package visibility before trying anonymous pull.
We will handle the first pull/visibility step after successful publication.

The scan reads an exported image archive, without Docker socket access. Evidence
artifacts retain the JSON report and small release record for seven days; the large
image archive is NOT uploaded as an Actions artifact. Authentication occurs after scans.

## Limitations and verification

Version and commit tags are conventions, not registry-enforced immutability.
Do not rerun an already published release to rebuild/overwrite it; use a new version.
Dependencies/base image still use floating ranges/tags, so rebuild reproducibility
requires a lock file and digest pinning. Third-party actions/tool images also need
reviewed SHA/digest pinning for hardened production usage.

Local integration test and first GHCR release are pending learner execution.

## Interview Q&A

- CI vs release? CI validates changes; release publishes a tested artifact.
- Why avoid rebuilding after tests? A fresh dependency resolution can produce different bytes.
- Why use digest deployment? It identifies image content even if someone changes a tag.
- Why a scanner gate? Prevent publishing images violating the configured severity policy.
- Where is the password? GitHub provides the job token; it is sent to login via stdin.

Sources: https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry
and https://github.com/anchore/grype/releases/tag/v0.120.0
