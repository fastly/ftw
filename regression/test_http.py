#from ftw import ruleset, http
import http
import ruleset

def main():
# protocol = 'http',
#                    dest_addr = 'localhost',
#                    port = 80,
#                    method = 'GET',
#                    uri = '/',
#                    version = 'HTTP/1.1',
#                    headers = {},
#                    data = '',
#                    status = 200,
    # Basic GET request - Should return 200 with <h1>Example Domain</h1>
    x = ruleset.Input(dest_addr="example.com",headers={"Host":"example.com"})
    http_ua = http.HttpUA(x)
    # issue web request
    print http_ua.send_request()[0]

    # Basic GET without Host on 1.1 - Expect 400 
    x = ruleset.Input(dest_addr="example.com",headers={})
    http_ua = http.HttpUA(x)
    print http_ua.send_request()[0]
    
    # Basic GET without Host on 1.0 - Expect 404 (server is VHosted)
    x = ruleset.Input(dest_addr="example.com",version="HTTP/1.0",headers={})
    http_ua = http.HttpUA(x)
    print http_ua.send_request()[0]
    
    # Basic GET wit Host on 1.0 - Expect 200
    x = ruleset.Input(dest_addr="example.com",version="HTTP/1.0",headers={"Host":"example.com"})
    http_ua = http.HttpUA(x)
    print http_ua.send_request()[0]

    # Basic GET without Host on 0.9 - Expect 505 version not supported
    x = ruleset.Input(dest_addr="example.com",version="HTTP/0.9",headers={})
    http_ua = http.HttpUA(x)
    print http_ua.send_request()[0]


main()
