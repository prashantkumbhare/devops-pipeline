# Deploy the trading API to AWS with Terraform

The existing GitHub Actions release job tests, scans and publishes the app. This
stack deploys the same public GHCR image by digest on one EC2 instance in
Singapore. It does not rebuild the app or change the release workflow.

Terraform provisions the VPC, subnet, internet gateway, security group,
instance profile and encrypted EC2 storage. EC2 bootstraps Docker, starts
PostgreSQL on a private Docker network, and starts FastAPI on host loopback
port 8000 only. The instance has outbound HTTPS and no inbound rules, including
SSH. Use AWS Systems Manager (SSM) for access without an SSH key. The database
password is generated on the host and is not in Terraform state or Git.

This is a single-AZ, disposable synthetic-data lab. Orders survive normal
restarts, but instance replacement or teardown deletes them. Updating the app
digest or moving to a newer AMI can replace the host. This is not a production
database or a publicly hosted API.

## Plan and apply

Use AWS CloudShell in Singapore or a Bash terminal with an authenticated AWS
CLI, Terraform 1.12 or another compatible 1.x release, Git and Python 3.
For local IAM Identity Center access, use your existing profile and sign in
with `aws sso login --profile <profile>`, then set `AWS_PROFILE`. Check the
AWS identity before running Terraform. The identity needs permissions to
provision the listed VPC, EC2 and IAM resources, pass the instance role, read
the public AMI parameter, and use SSM for verification and access.

If Terraform is missing in CloudShell on x86_64, install it into your home
directory (no sudo needed):

```bash
tf_version=1.12.2
tf_zip="terraform_${tf_version}_linux_amd64.zip"
tf_work=$(mktemp -d)
(
  set -e
  cd "$tf_work"
  tf_source="https://releases.hashicorp.com/terraform/$tf_version"
  curl -fsSLO "$tf_source/$tf_zip"
  curl -fsSLO "$tf_source/terraform_${tf_version}_SHA256SUMS"
  awk -v zip="$tf_zip" '$2 == zip' "terraform_${tf_version}_SHA256SUMS" | sha256sum -c -
  mkdir -p "$HOME/.local/bin"
  unzip -o "$tf_zip" terraform -d "$HOME/.local/bin"
)
rm -rf "$tf_work"
export PATH="$HOME/.local/bin:$PATH"
terraform version
```

From the repository root in the same shell:

```bash
aws sts get-caller-identity
terraform -chdir=infra/aws init
terraform -chdir=infra/aws plan -out=demo.tfplan
terraform -chdir=infra/aws apply demo.tfplan
bash infra/aws/smoke.sh
```

Terraform uses local state for this lab. Keep the original state directory
for subsequent updates and destruction. The smoke test waits for SSM and app
readiness, then checks liveness and creates and reads back one synthetic order.
Record the Terraform outputs and successful smoke-test output as demo evidence.
The AWS provider lock file is committed, but the plan and state are not.

Expect costs for the running t3.micro, the 12 GiB gp3 root volume, and public
IPv4, even though there are no inbound rules. No NAT gateway, load balancer
or RDS instance is provisioned. Check AWS pricing and available credits for
your account before leaving it running.

## Open Swagger UI from your laptop

With the AWS CLI and Session Manager plugin installed locally, use the same
AWS account and the instance ID from Terraform. Leave this command running.

```bash
aws ssm start-session --region ap-southeast-1 --target <instance-id> \
  --document-name AWS-StartPortForwardingSession \
  --parameters '{"portNumber":["8000"],"localPortNumber":["8000"]}'
```

Open [Swagger UI](http://127.0.0.1:8000/docs) or use
`curl http://127.0.0.1:8000/health/ready`. This localhost URL only works
while the local tunnel is open. Access is governed by IAM.

If bootstrapping fails, use the EC2 system log or an SSM shell session
to inspect `/var/log/cloud-init-output.log`,
`sudo journalctl -u trading-demo -b --no-pager`, and
`sudo docker logs trading-api` or `sudo docker logs trading-db`.

## Redeploy or clean up

For a new release or rollback, update `app_image` to the immutable GHCR digest
in that release's evidence, then run a fresh plan, apply and smoke test. Keep
the selected digest in tracked configuration if you want reproducible redeploys.
Review replacements in the plan because this lab does not retain orders across
host replacement.

From the same checkout and Terraform state, run
`terraform -chdir=infra/aws destroy` when done. Destroying the instance deletes
the demo database volume.
