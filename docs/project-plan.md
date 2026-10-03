# Trading application engineering interview lab

Status: planned; no application or deployment built yet.

## Outcomes

Build two independent GitHub repositories: devops-pipeline and trading-incident-assistant. Develop in installed VS Code with local Docker first; retain optional Codespaces configuration. Later deploy to a second laptop. Use synthetic trading data and public sources; no UBS code, incident data or internal documents.

## Delivery sequence

1. M1 — First working DevOps version: prerequisites, simulated trading API, PostgreSQL/Compose, reusable CI, published image and local deployment. Target first build session; completion depends on Docker readiness and GitHub publishing permissions.
2. M2 — Operate reliably: Codespaces option, rollback, controlled failures, metrics and alerts.
3. M3 — Infrastructure and multi-host practice: bounded Terraform lab, Ansible Linux target, second-laptop deployment, backup/restore.
4. A1 — First working AI version after M1: incident scenarios, shared pipeline, public HTTP adapters, linked article and actual model analysis. Model selection depends on available hardware.
5. A2 — Quality and review: explainable scores, evaluation, prompt injection cases, investigation UI and audit history.
6. A3 — Broader RAG after linked-article baseline evaluation.

## Architecture and ownership

DevOps repository owns shared workflows/deployment tooling and sample trading API. AI repository owns analysis application and calls shared workflows pinned to a reviewed commit SHA. Each produces a distinct image. Compose owns the application stack. Terraform exercises own separate resources. Ansible configures a Linux deployment target. The GitHub-hosted runner builds artifacts; a local deployment command pulls a selected release. Remote deployment automation is introduced only after target connectivity is established.

## Completion and learning

Every ticket has observable acceptance criteria, dependencies and interview vocabulary. Save real command outputs/screenshots where useful. Learner explains choices, makes one small modification and diagnoses a failure. Use measured results for interviews. A ticket closes only when acceptance criteria are verified; configuration alone does not prove Codespaces/cloud deployment works.

## Boundaries

No real trading or broker integration. No operational actions executed by the AI assistant. Secrets and Terraform state stay out of Git. Keep local ports bound to localhost initially. Free services have quotas; Codespaces is optional. Cloud deployment and Kubernetes are later extensions, not first-version requirements.

## Immediate next work

D01 → D02 → D03 → D05 → D06 → D07. D04 is optional and does not block local delivery.