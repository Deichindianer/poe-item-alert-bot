resource "aws_dynamodb_table" "poe_api_export_cache" {
  name         = "poe_api_export_cache"
  billing_mode = "PAY_PER_REQUEST"
  range_key    = "player_name"
  hash_key     = "player_league"

  attribute {
    name = "player_name"
    type = "S"
  }

  attribute {
    name = "player_league"
    type = "S"
  }
}
