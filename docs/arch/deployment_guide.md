# ChaloGhumo Multi-Cloud Deployment Guide

This guide outlines the requirements for activating the Continuous Deployment (CD) workflows for AWS, GCP, and Azure.

## 1. AWS Deployment (App Runner + ECR)

**Workflow**: `.github/workflows/cd-aws.yml`

### Required GitHub Secrets:
*   `AWS_ACCESS_KEY_ID`: IAM user with ECR and App Runner permissions.
*   `AWS_SECRET_ACCESS_KEY`: Corresponding secret key.
*   `AWS_APP_RUNNER_ROLE_ARN`: The ARN of the IAM role that App Runner uses to access ECR.

---

## 2. GCP Deployment (Cloud Run + Artifact Registry)

**Workflow**: `.github/workflows/cd-gcp.yml`

### Required GitHub Secrets:
*   `GCP_SA_KEY`: The JSON key for a Service Account with `Cloud Run Admin` and `Storage Admin` roles.
*   `GCP_PROJECT_ID`: Your Google Cloud Project ID.
*   `TOGETHER_API_KEY`: Required for the reasoning engine runtime.
*   `PROD_POSTGRES_SERVER`: The host of your production database.

---

## 3. Azure Deployment (Container Apps + ACR)

**Workflow**: `.github/workflows/cd-azure.yml`

### Required GitHub Secrets:
*   `AZURE_CREDENTIALS`: Output from `az ad sp create-for-rbac` (JSON format).
*   `AZR_REGISTRY_NAME`: The name of your Azure Container Registry (e.g., `chaloghumoregistry`).

---

## 4. Environment Variables

Ensure that your target deployment environments have the full suite of environment variables defined in `core/config.py`, including:
*   `TOGETHER_API_KEY`
*   `POSTGRES_*`
*   `QDRANT_*`
*   `REDIS_*`
*   `SNOWFLAKE_*` (if analytical persistence is enabled)

---
**Note**: All workflows are configured to trigger on pushes to the `main` branch. Manual triggers are also enabled via `workflow_dispatch`.
