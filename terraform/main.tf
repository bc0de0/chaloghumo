terraform {
  required_providers {
    snowflake = {
      source  = "Snowflake-Labs/snowflake"
      version = "~> 0.76"
    }
  }
}

provider "snowflake" {
  account  = var.snowflake_account
  username = var.snowflake_username
  password = var.snowflake_password
  role     = var.snowflake_role
}

# 1. Warehouse Provisioning
resource "snowflake_warehouse" "chaloghumo_wh" {
  name           = var.warehouse_name
  warehouse_size = "X-SMALL"
  auto_suspend   = 60
  auto_resume    = true
}

# 2. Database & Medallion Schemas
resource "snowflake_database" "chaloghumo_db" {
  name = var.database_name
}

resource "snowflake_schema" "bronze" {
  database = snowflake_database.chaloghumo_db.name
  name     = "RAW_BRONZE"
}

resource "snowflake_schema" "silver" {
  database = snowflake_database.chaloghumo_db.name
  name     = "CLEAN_SILVER"
}

resource "snowflake_schema" "gold" {
  database = snowflake_database.chaloghumo_db.name
  name     = "ANALYTICS_GOLD"
}

# 3. RBAC Roles
resource "snowflake_role" "etl_role" {
  name = "CHALOGHUMO_ETL_ROLE"
}

resource "snowflake_role" "reasoner_role" {
  name = "CHALOGHUMO_REASONER_ROLE"
}

# 4. Storage Integration (AWS S3)
resource "snowflake_storage_integration" "s3_integration" {
  name    = "S3_CHALOGHUMO_INTEGRATION"
  comment = "Integration for ChaloGhumo ETL Landing Zone"
  type    = "EXTERNAL_STAGE"

  enabled = true

  storage_allowed_locations = ["s3://${var.s3_bucket_name}/"]
  storage_provider         = "S3"
  storage_aws_role_arn     = "arn:aws:iam::000000000000:role/ChaloGhumoSnowflakeRole" # Dummy, DevOps to update
}

# 5. External Stage
resource "snowflake_stage" "raw_stage" {
  name                = "EXT_RAW_STAGE"
  url                 = "s3://${var.s3_bucket_name}/"
  database            = snowflake_database.chaloghumo_db.name
  schema              = snowflake_schema.bronze.name
  storage_integration = snowflake_storage_integration.s3_integration.name
}
