"""Upload a local file to S3."""
import argparse
import boto3

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--bucket", required=True)
    parser.add_argument("--file", required=True)
    parser.add_argument("--key", required=True)
    args = parser.parse_args()

    boto3.client("s3").upload_file(
        args.file,
        args.bucket,
        args.key,
    )
    print(f"Uploaded {args.file} to s3://{args.bucket}/{args.key}")
