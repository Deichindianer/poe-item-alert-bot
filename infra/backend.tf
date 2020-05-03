terraform {
  backend "s3" {
    bucket = "deichindianer-tf-state"
    key    = "poe-item-alert-bot/terraform.tfstate"
    region = "eu-central-1"
    acl    = "bucket-owner-full-control"
  }
}
