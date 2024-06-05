variable "src_path" {
  default     = "src"
  description = "The path to the source file to be zipped"
  type        = string
}

variable "python_filename" {
  description = "Name of the python file (no extension)"
  type        = string
}

variable "lambda_name" {
  description = "Name of the AWS lambda function"
  type        = string
}

variable "iam_role_arn" {
  description = "The ARN of the IAM role to attach to the lambda function"
  type        = string
}

variable "execution_arn" {
  description = "The execution ARN of the API Gateway"
  type        = string
}

variable "dynamodb_table_name" {
  description = "Name of the DynamoDB table"
  type        = string
}
