# Infrastructure Setup & DevOps Guide: ChaloGhumo Analytical Layer

## 1. Objective

This document provides the necessary configuration, system variables, and integration steps for a DevOps engineer to provision the ChaloGhumo infrastructure using Terraform.

**Note**: This guide assumes the use of **Snowflake** for the analytical layer and **AWS (S3)** as the primary ETL landing zone.

---

## 2. Prerequisites

### A. Snowflake Account

- **Account Admin** access for initial setup of Storage Integrations and Roles.
- **Snowflake Account URL** (e.g., `xy12345.us-east-1.snowflakecomputing.com`).

### B. AWS Account

- **IAM User/Role** with permissions to create S3 buckets and IAM policies.
- **Region**: Recommend `us-east-1` or consistent with the Snowflake deployment.

### C. Tools

- **Terraform** >= 1.5.0
- **AWS CLI** configured with appropriate credentials.

---

## 3. Configuration Variables (System-wide)

The following variables must be defined in your `terraform.tfvars` or CI/CD environment.

### Snowflake Infrastructure

| Variable | Description | Recommended Value |
| :--- | :--- | :--- |
| `snowflake_account` | Snowflake Account Identifier | `<ACCOUNT_ID>` |
| `snowflake_username` | Admin User for provisioning | `TF_USER` |
| `snowflake_role` | Initial setup role | `ACCOUNTADMIN` |
| `warehouse_size` | Default analytical warehouse size | `X-SMALL` |
| `auto_suspend` | Auto-suspend time in seconds | `60` |

### AWS Ingestion (ETL Source)

| Variable | Description | Value |
| :--- | :--- | :--- |
| `aws_region` | AWS Deployment Region | `us-east-1` |
| `s3_bucket_name` | Landing zone for raw travel data | `chaloghumo-raw-data-prod` |
| `iam_role_name` | Role for Snowflake Storage Integration | `ChaloGhumoSnowflakeRole` |

### External API Secrets

| Variable | Description | Source |
| :--- | :--- | :--- |
| `ticketmaster_api_key` | Events data access | [Developer Portal](https://developer.ticketmaster.com/) |
| `openweather_api_key` | Weather signal access | [OpenWeatherMap](https://openweathermap.org/api) |
| `predicthq_api_token` | Local demand signals | [PredictHQ](https://www.predicthq.com/) |

---

## 4. Secure Storage Integration (AWS <-> Snowflake)

Snowflake must be granted secure access to the S3 bucket via an **IAM Trust Relationship**.

### Step 1: Create IAM Policy in AWS

Provision an IAM policy that allows `s3:Get*`, `s3:List*`, and `s3:Put*` on the ingestion bucket.

### Step 2: Provision Snowflake Storage Integration

Use Terraform to create a `snowflake_storage_integration` resource. This will generate two critical values:

- `STORAGE_AWS_IAM_USER_ARN`
- `STORAGE_AWS_EXTERNAL_ID`

### Step 3: Update AWS IAM Trust Relationship

Apply the values from Step 2 to the AWS IAM Role's trust policy to finalize the handshake.

---

## 5. Sample `terraform.tfvars` Template

```hcl
# Snowflake Credentials
snowflake_account  = "org-account"
snowflake_username = "admin_user"
snowflake_role     = "ACCOUNTADMIN"

# Infrastructure Settings
database_name      = "CHALOGHUMO_DB"
warehouse_name     = "CHALOGHUMO_WH"
warehouse_size     = "X-SMALL"

# AWS Settings
aws_region         = "us-east-1"
s3_bucket_name     = "chaloghumo-etl-prod"

# API Keys (Recommend using AWS Secrets Manager or TF Variables)
ticketmaster_key   = "YOUR_KEY"
openweather_key    = "YOUR_KEY"
predicthq_token    = "YOUR_TOKEN"
```

---

## 6. Resources Provisioned

Upon successful execution of `terraform apply`, the following will be active:

1. **Snowflake Database** (`CHALOGHUMO_DB`).
2. **Medallion Schemas** (`RAW_BRONZE`, `CLEAN_SILVER`, `ANALYTICS_GOLD`).
3. **Auto-scaling Warehouse** (`CHALOGHUMO_WH`).
4. **External S3 Stage** linked via Storage Integration.
5. **Snowpipes** for automated ingestion from S3 to `RAW_BRONZE`.

---
**Status**: Ready for DevOps Execution.
