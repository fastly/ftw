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

    # Basic 
    x = ruleset.Input(dest_addr="example.com",headers={})
    http_ua = http.HttpUA(x)

    # check response and assert

main()
