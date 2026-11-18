variable "aws_region" {
  type        = string
  default     = "ap-southeast-1"
  description = "AWS Region for the demo and its Systems Manager commands."
}

variable "app_image" {
  type        = string
  default     = "ghcr.io/prashantkumbhare/trading-api@sha256:1ab56a9f409c429b5c70363999e8e9779d0ab1d08565ecfd846a4e62577bf576"
  description = "Immutable public digest of the tested GHCR release."

  validation {
    condition     = can(regex("^ghcr[.]io/prashantkumbhare/trading-api@sha256:[a-f0-9]{64}$", var.app_image))
    error_message = "Use an immutable sha256 digest from ghcr.io/prashantkumbhare/trading-api."
  }
}
