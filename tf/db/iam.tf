# auth_service/iam.tf

resource "aws_iam_role" "service_role" {
  name = "auth_service_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = "sts:AssumeRole",
      Effect = "Allow",
      Principal = {
        Service = "ec2.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_policy" "lambda_invoke_policy" {
  name = "lambda_invoke_policy"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Action = [
        "lambda:InvokeFunction"
      ],
      Resource = var.manage_db_resources_lambda_arn
    }]
  })
}

resource "aws_iam_role_policy_attachment" "attach_lambda_invoke_policy" {
  role       = aws_iam_role.service_role.name
  policy_arn = aws_iam_policy.lambda_invoke_policy.arn
}
