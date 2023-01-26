if __name__ == '__main__':
    # Importing eventlet.green.http.client after http.client was already imported
    # used to change the original http/http.client, that was breaking things.
    import http.client
    original_id = id(http.client)
    import eventlet.green.http.client  # noqa
    assert id(http.client) == original_id
    print('pass')
