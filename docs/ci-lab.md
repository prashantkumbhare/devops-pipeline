# CI: automate the experiments

## Quick reference

From Git Bash: `bash scripts/test-ci.sh`.
Docker Desktop must be running. No Windows Python installation is required.
The test uses a separate trading-ci project, trading-api:ci image, internal ports,
and disposable volume. Cleanup deletes only that test project's containers/volume.
Do not put valuable data in trading-ci. The interactive devops-pipeline stack remains separate.

## What runs

1. Build the image and wait for API/database health.
2. Check creation 201, exact lookup, invalid quantity 422 without insertion, missing ID 404.
3. Restart API and verify the single stored test order.
4. Remove/recreate containers, retaining test volume, and verify persistence.
5. Stop database; check liveness 200 and readiness/orders 503.
6. Start database; verify service recovery and stored order.
7. Clean up the disposable test stack even when a check fails.

compose.ci.yaml overrides host port publishing, so the test doesn't collide with
your running application. Its test container runs standard-library Python HTTP
assertions against api:8000. Failed assertions return nonzero and fail the job.

## Pipeline vocabulary

Workflow: automation defined in YAML. Trigger: push or pull request event.
Job: work on a runner. Runner: GitHub's Ubuntu machine with Docker.
Step: checkout or run a command. Checkout: obtain this run's source code.
CI: build and test integration automatically; it is not deployment.

ci.yaml calls reusable-ci.yaml through workflow_call. The shared workflow checks
out the calling repository and executes its checked-in test script. The future AI
repository can supply its own script and call this workflow at a reviewed commit SHA.
The tests remain application-specific. Token access is contents:read; no personal
token or local .env secret is uploaded. Concurrency cancels superseded branch/PR runs.

The first pipeline doesn't publish an image or deploy to your laptop. Release
artifacts, scanning, dependency locks and pinned image/action digests are later work.
Local and GitHub execution are pending until the learner runs and pushes these files.

## Interview Q&A

- Why test the running image? It catches packaging/network/database integration failures.
- Why isolate tests? They stop/recreate a database and clean up disposable data.
- Why reuse workflows? Share orchestration while each application owns its tests.
- Why keep the script runnable locally? Reproduce CI failures with the same steps.

Source: https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows
