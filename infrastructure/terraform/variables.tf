variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "eu-north-1"  
}

variable "ami_id" {
  description = "AMI ID for EC2 instance (Ubuntu Server)"
  type        = string
  default     = "ami-0fe8bec493a81c7da"  
}

variable "vpc_id" {
  description = "Existing VPC ID"
  type        = string
  default     = "vpc-05697684a7d22af0a"
}

variable "key_name" {
  description = "Name of the SSH key pair"
  type        = string
}