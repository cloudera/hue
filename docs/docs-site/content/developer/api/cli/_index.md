---
title: "CLI"
date: 2020-09-08T00:00:00-07:00
draft: false
weight: 2
---

Easily leverage the Query Service via the CLI.

- Execute an SQL statement or saved query
- List, download, upload files


Install from https://pypi.org/project/gethue/:

    pip install gethue

And use:

    > compose --help

    > compose auth

    Api url [https://demo.gethue.com]:
    Username [demo]:
    Password [demo]:
    Auth: success 200
    Token: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjMxMjE5MDkxLCJqdGkiOiJkNGJkY2Q5M2NjMjg0MDlkYWJlYWZhNGRlNjlkOTMzMyIsInVzZXJfaWQiOjJ9.Gr8bW_JaZ8yzQ3eEZYp3jKbdsSgLAXxqvSRbeU6jhLg

List remote storage files:

    compose storage list s3a://demo-gethue
