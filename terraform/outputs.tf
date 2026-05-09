output "storage_integration_iam_user_arn" {
  description = "AWS IAM User ARN for Snowflake Storage Integration"
  value       = snowflake_storage_integration.s3_integration.storage_aws_iam_user_arn
}

output "storage_integration_external_id" {
  description = "External ID for the AWS IAM Trust Relationship"
  value       = snowflake_storage_integration.s3_integration.storage_aws_external_id
}

output "warehouse_name" {
  value = snowflake_warehouse.chaloghumo_wh.name
}

output "database_name" {
  value = snowflake_database.chaloghumo_db.name
}
