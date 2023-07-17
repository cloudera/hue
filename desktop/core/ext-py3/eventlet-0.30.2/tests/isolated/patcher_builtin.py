if __name__ == '__main__':
    from tests.mock import patch

    import sys
    import eventlet
    from eventlet import hubs
    with patch.object(hubs, 'notify_opened') as mock_func:
        eventlet.monkey_patch(builtins=True)
        with open(__file__, 'r') as f:
            mock_func.assert_called_with(f.fileno())
        if sys.version_info.major == 2:
            with file(__file__, 'r') as f:
                mock_func.assert_called_with(f.fileno())
    print('pass')
