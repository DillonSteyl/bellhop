data "archive_file" "lambda_archive" {
  type        = "zip"
  source_file = "./${var.src_path}/${var.python_filename}.py"
  output_path = "${var.python_filename}.zip"
}

resource "aws_lambda_function" "lambda" {
  filename      = data.archive_file.lambda_archive.output_path
  function_name = var.lambda_name
  role          = var.iam_role_arn

  source_code_hash = data.archive_file.lambda_archive.output_base64sha256

  runtime = "python3.12"
  handler = "${var.python_filename}.lambda_handler"

  environment {
    variables = {
      TABLE_NAME = var.dynamodb_table_name
    }
  }
}

resource "aws_lambda_permission" "allow_apigateway_invoke" {
  statement_id  = "AllowWebsocketInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda.function_name
  principal     = "apigateway.amazonaws.com"

  # The /* part allows invocation from any stage, method and resource path
  # within API Gateway.
  source_arn = "${var.execution_arn}/*"
}
