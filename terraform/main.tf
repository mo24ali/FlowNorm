provider "aws" {
  region = "us-east-1"
}

# --- VPC & Networking ---
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  name   = "fintech-mvp-vpc"
  cidr   = "10.0.0.0/16"

  azs             = ["us-east-1a", "us-east-1b"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24"]

  enable_nat_gateway = true
}

# --- RDS PostgreSQL Instance ---
resource "aws_db_instance" "fintech_db" {
  identifier           = "fintech-postgres"
  engine               = "postgres"
  engine_version       = "15.3"
  instance_class       = "db.t3.micro" # MVP Free Tier eligible
  allocated_storage     = 20
  db_name              = "fintech_db"
  username             = "admin"
  password             = "Fintech2024Secure!" # Use SSM Parameter in production
  parameter_group_name = "default.postgres15"
  skip_final_snapshot  = true
  
  vpc_security_group_ids = [aws_security_group.db_sg.id]
  db_subnet_group_name   = module.vpc.database_subnet_group
}

# --- Lambda Data Normalizer ---
resource "aws_lambda_function" "normalizer" {
  filename      = "lambda_payload.zip"
  function_name = "fintech_data_normalizer"
  role          = aws_iam_role.lambda_exec.arn
  handler       = "main.handler"
  runtime       = "python3.11"
  environment {
    variables = {
      DATABASE_URL = "postgresql://admin:Fintech2024Secure!@${aws_db_instance.fintech_db.address}/fintech_db"
    }
  }
}

# --- IAM Role for Lambda ---
resource "aws_iam_role" "lambda_exec" {
  name = "lambda_exec_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

# Security Group for Database
resource "aws_security_group" "db_sg" {
  name        = "fintech_db_sg"
  vpc_id      = module.vpc.vpc_id
  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"] # Only VPC access
  }
}

# --- Outputs ---
output "db_endpoint" {
  value = aws_db_instance.fintech_db.endpoint
}
