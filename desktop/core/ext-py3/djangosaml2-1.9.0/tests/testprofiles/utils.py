def csp_handler(response):
    response.headers["Content-Security-Policy"] = "testing CSP value"
    return response
