provider "aws" {
  region = var.aws_region
}

resource "aws_vpc" "mlops_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "mlops-vpc"
    Project = "mlops-free-tier"
  }
}

resource "aws_subnet" "public" {
  vpc_id            = aws_vpc.mlops_vpc.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "${var.aws_region}a"
  map_public_ip_on_launch = true

  tags = {
    Name = "mlops-public-subnet"
    Project = "mlops-free-tier"
  }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.mlops_vpc.id

  tags = {
    Name = "mlops-igw"
    Project = "mlops-free-tier"
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.mlops_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name = "mlops-public-rt"
    Project = "mlops-free-tier"
  }
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

resource "aws_security_group" "mlops_sg" {
  name        = "mlops-security-group"
  description = "Security group for MLOps server"
  vpc_id      = aws_vpc.mlops_vpc.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # MLflow
  ingress {
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Prometheus 
  ingress {
    from_port   = 9090
    to_port     = 9090
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Grafana 
  ingress {
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "mlops-sg"
    Project = "mlops-free-tier"
  }
}

resource "aws_instance" "mlops_server" {
  ami           = var.ami_id  # Ubuntu Server 22.04 LTS (ami-03318bd22f0010746 pour eu-west-3)
  instance_type = "t2.micro"
  subnet_id     = aws_subnet.public.id

  vpc_security_group_ids = [aws_security_group.mlops_sg.id]
  key_name              = var.key_name

  root_block_device {
    volume_size = 29  # < 30go limite free tier
    volume_type = "gp2"
  }

  tags = {
    Name = "mlops-server"
    Project = "mlops-free-tier"
  }
}

resource "aws_s3_bucket" "mlops_bucket" {
  bucket = "mlops-${random_string.suffix.result}"

  tags = {
    Name = "mlops-bucket"
    Project = "mlops-free-tier"
  }
}

resource "aws_s3_bucket_versioning" "mlops_bucket" {
  bucket = aws_s3_bucket.mlops_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "random_string" "suffix" {
  length  = 8
  special = false
  upper   = false
}