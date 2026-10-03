#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
# Dedicated project, image and internal-only ports protect the interactive lab.
# The disposable test password is not a user credential.
export POSTGRES_PASSWORD=disposable-ci-lab-only
compose() {
  docker compose --env-file .env.example -p trading-ci -f compose.yaml -f compose.ci.yaml "$@"
}
cleanup() {
  result=$?
  trap - EXIT
  if [ "$result" -ne 0 ]; then compose logs --no-color --tail 100 api db; fi
  compose down -v --remove-orphans
  exit "$result"
}
trap cleanup EXIT
# Reset only this explicitly named disposable test project.
compose down -v --remove-orphans
compose up -d --build --wait --wait-timeout 120
compose run --rm test create
compose restart api
compose run --rm test persist
compose down
compose up -d --wait --wait-timeout 120
compose run --rm test persist
compose stop db
compose run --rm test outage
compose start db
compose run --rm test persist
echo "All integration checks passed."
