variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "eu-west-1"  
}

variable "ami_id" {
  description = "AMI ID for EC2 instance (Ubuntu Server)"
  type        = string
  default     = "ami-0694d931cee176e7d"  
}

variable "vpc_id" {
  description = "Existing VPC ID"
  type        = string
  default     = "vpc-04046db55268c9875"
}

variable "key_name" {
  description = "Name of the SSH key pair"
  type        = string
}