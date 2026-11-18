#!/usr/bin/env bash
set -euo pipefail
export AWS_PAGER=""

stack_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
instance=$(terraform -chdir="$stack_dir" output -raw instance_id)
region=$(terraform -chdir="$stack_dir" output -raw aws_region)

for ((i = 1; i <= 60; i++)); do
  ping_status=$(aws ssm describe-instance-information --region "$region" \
    --filters "Key=InstanceIds,Values=$instance" \
    --query 'InstanceInformationList[0].PingStatus' --output text)
  [[ "$ping_status" != Online ]] || break
  if ((i == 60)); then
    echo "Instance $instance did not register with SSM. Check the EC2 system log and instance profile." >&2
    exit 1
  fi
  sleep 5
done

params=$(python3 - "$stack_dir/smoke.py" <<'PY'
import json
from pathlib import Path
import sys

script = Path(sys.argv[1]).read_text()
print(json.dumps({
    "commands": ["python3 - <<'PYTHON_SMOKE'\n" + script + "\nPYTHON_SMOKE"],
    "executionTimeout": ["540"],
}))
PY
)
command_id=$(aws ssm send-command --region "$region" --instance-ids "$instance" \
  --document-name AWS-RunShellScript --parameters "$params" \
  --comment "Trading demo smoke test" --query 'Command.CommandId' --output text)
printf 'SSM command %s on %s\n' "$command_id" "$instance"

err=$(mktemp)
trap 'rm -f "$err"' EXIT
for ((i = 1; i <= 120; i++)); do
  if status=$(aws ssm get-command-invocation --region "$region" --instance-id "$instance" \
    --command-id "$command_id" --query Status --output text 2>"$err"); then
    case "$status" in
      Pending|InProgress|Delayed|Cancelling) ;;
      *)
        aws ssm get-command-invocation --region "$region" --instance-id "$instance" \
          --command-id "$command_id" \
          --query '{status:Status,output:StandardOutputContent,error:StandardErrorContent}' --output json
        [[ "$status" == Success ]]
        exit
        ;;
    esac
  elif ! grep -q 'InvocationDoesNotExist' "$err"; then
    cat "$err" >&2
    exit 1
  fi
  sleep 5
done
echo "Timed out waiting for SSM command $command_id" >&2
exit 1
