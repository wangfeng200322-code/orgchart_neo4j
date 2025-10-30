#!/usr/bin/env python3
"""
Create a strong admin API key and optionally store it in AWS SSM Parameter Store.

Usage:
  python scripts/create_admin_api_key.py --store
  python scripts/create_admin_api_key.py --print

Options:
  --name NAME   Parameter name (default: orgchart_admin_api_key)
  --store       Store the generated key in SSM using boto3 (requires AWS creds)
  --region REG  AWS region (default: us-east-1)

This script uses the `secrets` module to generate a 48-character URL-safe key.
"""
import argparse
import secrets
import boto3
import sys

DEFAULT_NAME = "orgchart_admin_api_key"

parser = argparse.ArgumentParser()
parser.add_argument('--name', default=DEFAULT_NAME)
parser.add_argument('--store', action='store_true', help='Store key in SSM Parameter Store')
parser.add_argument('--region', default='us-east-1')
args = parser.parse_args()

key = secrets.token_urlsafe(48)
print(f"Generated key: {key}")

if args.store:
    try:
        ssm = boto3.client('ssm', region_name=args.region)
        ssm.put_parameter(
            Name=args.name,
            Value=key,
            Type='SecureString',
            Overwrite=True
        )
        print(f"Stored key in SSM parameter: {args.name} (region={args.region})")
    except Exception as e:
        print(f"Failed to store key in SSM: {e}")
        sys.exit(2)
else:
    print("Run with --store to save into SSM (requires AWS credentials)")
