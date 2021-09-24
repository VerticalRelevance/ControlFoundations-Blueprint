package s3_bucket_encryption

compliant {
    some resource
    input.Resources[resource].Type == "AWS::S3::Bucket"
    input.Resources[resource].Properties.BucketEncryption.ServerSideEncryptionConfiguration[_].ServerSideEncryptionByDefault.SSEAlgorithm
}