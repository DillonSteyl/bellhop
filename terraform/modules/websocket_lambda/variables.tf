variable "handler_filename" {
  description = "Name of the python file (no extension)"
  type        = string
  default     = "handlers"
}

variable "handler_function_name" {
  description = "Name of the handler function in the python file"
  type        = string
}

variable "archive_folder" {
  description = "Archive file containing the lambda function code"
  type = object({
    output_path         = string
    output_base64sha256 = string
  })
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

variable "deployed_environment" {
  description = "The environment the lambda function is deployed to"
  type        = string
  default     = "production"
}
