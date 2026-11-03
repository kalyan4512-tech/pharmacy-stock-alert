provider "aws" {
  region = "us-east-1"
}

# Find the default VPC
data "aws_vpc" "default" {
  default = true
}

# Find a subnet in the default VPC
data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# Security Group
resource "aws_security_group" "pharmacy_sg" {
  name        = "pharmacy-stock-sg"
  description = "Security group for Pharmacy Stock Alert System"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "SSH access - restrict to your IP before applying"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["157.51.77.152/32"]
  }

  ingress {
    description = "Pharmacy application"
    from_port   = 5001
    to_port     = 5001
    protocol    = "tcp"
    cidr_blocks = ["157.51.77.152/32"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# EC2 Instance
resource "aws_instance" "pharmacy_server" {
  ami                         = "ami-0c02fb55956c7d316"
  instance_type               = "t3.micro"
  iam_instance_profile        = aws_iam_instance_profile.pharmacy_ssm_profile.name
  subnet_id                   = "subnet-03fba7788dec58cbc"
  vpc_security_group_ids      = [aws_security_group.pharmacy_sg.id]
  associate_public_ip_address = true

  tags = {
    Name        = "Pharmacy-Stock-Server"
    Project     = "Pharmacy-Stock-Alert"
    Environment = "Development"
  }
}
resource "aws_iam_instance_profile" "pharmacy_ssm_profile" {
  name = "Pharmacy-EC2-SSM-Profile"
  role = "Pharmacy-EC2-SSM-Role"
}

# Output public IP
output "pharmacy_server_public_ip" {
  value = aws_instance.pharmacy_server.public_ip
}
