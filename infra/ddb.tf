resource "aws_dynamodb_table" "poe_api_export_cache" {
  name         = "poe_api_export_cache"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "player_name"

  attribute {
    name = "player_name"
    type = "S"
  }
}
