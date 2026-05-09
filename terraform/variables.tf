variable "snowflake_account" {
  description = "Snowflake Account Identifier"
  type        = string
}

variable "snowflake_username" {
  description = "Snowflake Username"
  type        = string
}

variable "snowflake_password" {
  description = "Snowflake Password"
  type        = string
  sensitive   = true
}

variable "snowflake_role" {
  description = "Role to use for provisioning (recommend ACCOUNTADMIN)"
  type        = string
  default     = "ACCOUNTADMIN"
}

variable "aws_region" {
  description = "AWS Region for S3 Bucket"
  type        = string
  default     = "us-east-1"
}

variable "s3_bucket_name" {
  description = "AWS S3 Bucket for raw data ingestion"
  type        = string
}

variable "warehouse_name" {
  description = "Name of the Snowflake Warehouse"
  type        = string
  default     = "CHALOGHUMO_WH"
}

variable "database_name" {
  description = "Name of the Snowflake Database"
  type        = string
  default     = "CHALOGHUMO_DB"
}
