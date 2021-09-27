package s3_bucket_encryption

compliant {
    some resource
    input.Resources[resource].Type == "AWS::S3::Bucket"
    input.Resources[resource].Properties.BucketEncryption.ServerSideEncryptionConfiguration[_].ServerSideEncryptionByDefault.SSEAlgorithm
} else = false {
    # Fail if buckets but not encrypted
    some resource
    input.Resources[resource].Type == "AWS::S3::Bucket"
} else = true # Succeed if no buckets