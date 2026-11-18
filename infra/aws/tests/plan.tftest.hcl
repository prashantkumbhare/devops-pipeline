mock_provider "aws" {
  mock_data "aws_ssm_parameter" {
    defaults = { value = "ami-0123456789abcdef0" }
  }
  mock_data "aws_partition" {
    defaults = { partition = "aws" }
  }
}

run "demo_plan" {
  command = plan

  assert {
    condition     = aws_instance.demo.metadata_options[0].http_tokens == "required" && aws_instance.demo.root_block_device[0].encrypted
    error_message = "Expected IMDSv2 and encrypted root storage"
  }

  assert {
    condition     = strcontains(aws_instance.demo.user_data, var.app_image) && strcontains(aws_instance.demo.user_data, "127.0.0.1:8000:8000")
    error_message = "Expected pinned image and loopback-only API"
  }

  assert {
    condition     = aws_vpc_security_group_egress_rule.https.from_port == 443 && aws_vpc_security_group_egress_rule.https.to_port == 443
    error_message = "Expected HTTPS egress"
  }
}
