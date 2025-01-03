provider "aws" {
  region = var.aws_region
}

data "aws_vpc" "existing" {
  id = var.vpc_id
}

resource "aws_subnet" "public" {
  vpc_id            = data.aws_vpc.existing.id
  cidr_block        = "172.31.128.0/24"
  availability_zone = "${var.aws_region}a"
  map_public_ip_on_launch = true

  tags = {
    Name = "mlops-public-subnet"
    Project = "mlops-free-tier"
  }
}

resource "random_string" "suffix" {
  length  = 8
  special = false
  upper   = false
}

data "aws_internet_gateway" "existing" {
  filter {
    name   = "attachment.vpc-id"
    values = [var.vpc_id]
  }
}

resource "aws_route_table" "public" {
  vpc_id = data.aws_vpc.existing.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = data.aws_internet_gateway.existing.id
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

resource "aws_iam_role" "ec2_role" {
  name = "main_mlops_ec2_role_${random_string.suffix.result}"  

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  path = "/main/"  

  tags = {
    Project = "mlops-free-tier"
    Group = "Main"
  }
}

resource "aws_iam_role_policy" "comprehend_s3_ecr_access" {
  name = "main_comprehend_s3_ecr_access"
  role = aws_iam_role.ec2_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ]
        Resource = [
          "${aws_s3_bucket.mlops_bucket.arn}",
          "${aws_s3_bucket.mlops_bucket.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "comprehend:DetectSentiment",
          "comprehend:DetectEntities",
          "comprehend:DetectKeyPhrases"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:GetRepositoryPolicy",
          "ecr:DescribeRepositories",
          "ecr:ListImages",
          "ecr:DescribeImages",
          "ecr:BatchGetImage",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload",
          "ecr:PutImage"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_instance_profile" "mlops_profile" {
  name = "main_mlops_profile"  # Ajout du préfixe main
  role = aws_iam_role.ec2_role.name
  path = "/main/"  # Ajout du path pour correspondre au groupe Main
}

resource "aws_security_group" "mlops_sg" {
  name        = "mlops-security-group-${random_string.suffix.result}"
  description = "Security group for MLOps server"
  vpc_id      = data.aws_vpc.existing.id

  # SSH
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "API access"
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
  ami           = var.ami_id
  instance_type = "t2.micro"
  subnet_id     = aws_subnet.public.id
  iam_instance_profile = aws_iam_instance_profile.mlops_profile.name

  vpc_security_group_ids = [aws_security_group.mlops_sg.id]
  key_name              = var.key_name

  root_block_device {
    volume_size = 29  # < 30go
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

output "server_public_ip" {
  value = aws_instance.mlops_server.public_ip
  description = "L'adresse IP publique de l'instance EC2"
}

output "s3_bucket_name" {
  value = aws_s3_bucket.mlops_bucket.bucket
  description = "Le nom du bucket S3"
}

output "mlflow_url" {
  value = "http://${aws_instance.mlops_server.public_ip}:5000"
  description = "L'URL de MLflow"
}

