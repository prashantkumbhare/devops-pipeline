output "instance_id" {
  value = aws_instance.demo.id
}

output "aws_region" {
  value = var.aws_region
}

output "app_image" {
  value = var.app_image
}
