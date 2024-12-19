variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "eu-west-3"  # Europe (Paris)
}

variable "ami_id" {
  description = "AMI ID for EC2 instance (Ubuntu Server)"
  type        = string
  default     = "ami-03318bd22f0010746"  # Ubuntu 22.04 LTS eu-west-3
}

variable "key_name" {
  description = "Name of the SSH key pair"
  type        = string
}

# outputs.tf
output "server_public_ip" {
  value = aws_instance.mlops_server.public_ip
}

output "s3_bucket_name" {
  value = aws_s3_bucket.mlops_bucket.bucket
}