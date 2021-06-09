
## hue.ini

    [desktop]
    [[raz]]
    ## Turns on the integration as ready to use
    is_enabled=true

    ## Endpoint to contact
    # api_url=https://localhost:8080

    ## How to authenticate against: KERBEROS or JWT (not supported yet)
    # api_authentication=KERBEROS


## RAZ Hue Clients

Located in [desktop/core/src/desktop/lib/raz/clients_test.py](/desktop/core/src/desktop/lib/raz/clients_test.py).

    ./build/env/bin/hue test specific desktop.lib.raz.clients_test


## File Systems going via RAZ

Located in [desktop/libs/aws/src/aws/s3/s3connection.py](/desktop/libs/aws/src/aws/s3/s3connection.py).

    TEST_S3_BUCKET=gethue-test ./build/env/bin/hue test specific aws.s3.s3connection_test

  GET 'get_all_buckets'
  GET 'gethue-test'
  GET 'gethue-test/data/query-hive-weblogs.csv'


## Boto 3

If we need to improve RAZ to generate signed request for listing keys with prefixes:

    https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-presigned-urls.html#using-presigned-urls-to-perform-other-s3-operations
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.list_objects
