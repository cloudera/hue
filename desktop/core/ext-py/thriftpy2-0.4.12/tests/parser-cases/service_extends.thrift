include "shared.thrift"


service PingService extends shared.SharedService {
    string ping()
}
