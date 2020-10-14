struct User {
    1: required string name,
    2: optional string avatar 
}

struct Post {
    1: required string title,
    2: required string content,
    3: required User user,
}

const Post post = {'title': 'hello world', 'content': 'hello', 
    'user': {}}
