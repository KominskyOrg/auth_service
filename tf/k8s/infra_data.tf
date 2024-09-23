data "terraform_remote_state" "infrastructure" {
  backend = "s3"
  config = {
    bucket         = "tf-statelock"
    key            = "kom_aws_tf.tfstate"
    region         = "us-east-1"
    dynamodb_table = "tf-state-table"
  }
}
