#!/usr/bin/env python3
"""
Rotate the admin API key stored in AWS SSM Parameter Store.

Usage:
  python scripts/rotate_admin_api_key.py --name orgchart_admin_api_key --region us-east-1

This will generate a new API key, overwrite the existing SSM SecureString parameter, and optionally print the new key.
Note: You must have AWS credentials with permission to put_parameter for the specified name.
"""
import argparse
import secrets
import boto3
import sys

DEFAULT_NAME = "orgchart_admin_api_key"

parser = argparse.ArgumentParser()
parser.add_argument('--name', default=DEFAULT_NAME)
parser.add_argument('--region', default='eu-central-1')
parser.add_argument('--print', dest='print_key', action='store_true', help='Print the new key to stdout')
args = parser.parse_args()

new_key = secrets.token_urlsafe(48)

try:
    ssm = boto3.client('ssm', region_name=args.region)
    ssm.put_parameter(
        Name=args.name,
        Value=new_key,
        Type='SecureString',
        Overwrite=True
    )
    print(f"Rotated key stored in SSM parameter: {args.name} (region={args.region})")
    if args.print_key:
        print(f"New key: {new_key}")
except Exception as e:
    print(f"Failed to rotate key in SSM: {e}")
    sys.exit(2)
