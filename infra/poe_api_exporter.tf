data "archive_file" "poe_api_exporter" {
  type        = "zip"
  source_dir  = "../src/poe-api-exporter"
  output_path = "../src/poe-api-exporter.zip"
}

resource "aws_lambda_function" "poe_api_exporter" {
  filename         = "../src/poe-api-exporter.zip"
  function_name    = "poe-api-exporter"
  description      = "Exports the poe character window API into a cache"
  role             = aws_iam_role.poe_api_exporter.arn
  handler          = "handler.handler"
  source_code_hash = data.archive_file.poe_api_exporter.output_base64sha256
  runtime          = "python3.7"
  timeout          = 300
  memory_size      = 512
  tags             = merge(var.tags, map("Name", "poe-api-exporter", "Component", "poe_api_exporter"))

  depends_on = [data.archive_file.poe_api_exporter]
}

### Lambda ###
resource "aws_iam_role" "poe_api_exporter" {
  name               = "poe_api_exporter_execution"
  assume_role_policy = file("policies/lambda_assume_role.json")
  tags               = merge(var.tags, map("Name", "poe_api_exporter_execution", "Component", "poe_api_exporter"))
}

resource "aws_iam_policy" "poe_api_exporter" {
  name        = "poe_api_exporter_execution"
  description = "Allow the api export to write to DDB and get from the parameter store"
  policy      = file("policies/poe_api_exporter_execution.json")
}

resource "aws_iam_role_policy_attachment" "poe_api_exporter" {
  role       = aws_iam_role.poe_api_exporter.name
  policy_arn = aws_iam_policy.poe_api_exporter.arn
}

resource "aws_iam_role_policy_attachment" "poe_api_exporter_lambda_basic_execution" {
  role       = aws_iam_role.poe_api_exporter.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}
