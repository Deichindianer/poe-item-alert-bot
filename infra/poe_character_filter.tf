data "archive_file" "poe_character_filter" {
  type        = "zip"
  source_dir  = "../src/poe-character-filter"
  output_path = "../src/poe-character-filter.zip"
}

resource "aws_lambda_function" "poe_character_filter" {
  filename         = "../src/poe-character-filter.zip"
  function_name    = "poe-character-filter"
  description      = "Doing the filtering magic"
  role             = aws_iam_role.poe_character_filter.arn
  handler          = "handler.handler"
  source_code_hash = data.archive_file.poe_character_filter.output_base64sha256
  runtime          = "python3.7"
  timeout          = 300
  memory_size      = 512
  tags             = merge(var.tags, map("Name", "poe-character-filter", "Component", "poe_character_filter"))

  depends_on = [data.archive_file.poe_character_filter]
}

### Lambda ###
resource "aws_iam_role" "poe_character_filter" {
  name               = "poe_character_filter_execution"
  assume_role_policy = file("policies/lambda_assume_role.json")
  tags               = merge(var.tags, map("Name", "poe_character_filter_execution", "Component", "poe_character_filter"))
}

resource "aws_iam_policy" "poe_character_filter" {
  name        = "poe_character_filter_execution"
  description = "Allow the api export to write to DDB and get from the parameter store"
  policy      = file("policies/poe_character_filter_execution.json")
}

resource "aws_iam_role_policy_attachment" "poe_character_filter" {
  role       = aws_iam_role.poe_character_filter.name
  policy_arn = aws_iam_policy.poe_character_filter.arn
}

resource "aws_iam_role_policy_attachment" "poe_character_filter_lambda_basic_execution" {
  role       = aws_iam_role.poe_character_filter.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}
