struct User {
    1: string name,
    2: string address,
}

struct Email {
    1: string subject,
    2: string content,
}

exception NetworkError {
    1: string message,
    2: i32 http_code
}

service EmailService {
    void ping () 
        throws (1: NetworkError network_error)
    bool send(1: User recver, 2: User sender, 3: Email email)
        throws (1: NetworkError network_error)
}
