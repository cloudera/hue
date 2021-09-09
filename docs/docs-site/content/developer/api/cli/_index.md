---
title: "CLI"
date: 2020-09-08T00:00:00-07:00
draft: false
weight: 2
---

A wrapper around the REST API.

Install:

    pip install gethue

And use:

    > compose --help

    > compose auth

    Api url [https://demo.gethue.com]:
    Username [demo]:
    Password [demo]:
    Auth: success 200
    Token: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjMxMjE5MDkxLCJqdGkiOiJkNGJkY2Q5M2NjMjg0MDlkYWJlYWZhNGRlNjlkOTMzMyIsInVzZXJfaWQiOjJ9.Gr8bW_JaZ8yzQ3eEZYp3jKbdsSgLAXxqvSRbeU6jhLg

    > compose query

  > compose query autocomplete

List, view, download, upload files:

    compose storage list s3a://demo-gethue
