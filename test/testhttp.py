from ftw import ruleset, http
#import http
#import ruleset

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
def test1():
    x = ruleset.Input(dest_addr="example.com",headers={"Host":"example.com"})
    http_ua = http.HttpUA(x)
    # issue web request
    http_ua.send_request()
    assert http_ua.response_object.status == 200
  
    
def test2():
    # Basic GET without Host on 1.1 - Expect 400 
    x = ruleset.Input(dest_addr="example.com",headers={})
    http_ua = http.HttpUA(x)
    http_ua.send_request()
    assert http_ua.response_object.status == 400

def test3():    
    # Basic GET without Host on 1.0 - Expect 404 (server is VHosted)
    x = ruleset.Input(dest_addr="example.com",version="HTTP/1.0",headers={})
    http_ua = http.HttpUA(x)
    http_ua.send_request()
    assert http_ua.response_object.status == 404

def test4():    
    # Basic GET wit Host on 1.0 - Expect 200
    x = ruleset.Input(dest_addr="example.com",version="HTTP/1.0",headers={"Host":"example.com"})
    http_ua = http.HttpUA(x)
    http_ua.send_request()
    assert http_ua.response_object.status == 200

def test5():
    # Basic GET without Host on 0.9 - Expect 505 version not supported
    x = ruleset.Input(dest_addr="example.com",version="HTTP/0.9",headers={})
    http_ua = http.HttpUA(x)
    http_ua.send_request()
    assert http_ua.response_object.status == 505
    
def test6():
    # Basic GET without Host with invalid version (request line) - Expect 400 invalid
    x = ruleset.Input(dest_addr="example.com",version="HTTP/1.0 x",headers={})
    http_ua = http.HttpUA(x)
    http_ua.send_request()
    assert http_ua.response_object.status == 400

def test7():
    # TEST method which doesn't exist - Expect 501
    x = ruleset.Input(method="TEST",dest_addr="example.com",version="HTTP/1.0",headers={})
    http_ua = http.HttpUA(x)
    http_ua.send_request()
    assert http_ua.response_object.status == 501

def test8():
    # PROPFIND method which isn't allowed - Expect 405
    x = ruleset.Input(method="PROPFIND",dest_addr="example.com",version="HTTP/1.0",headers={})
    http_ua = http.HttpUA(x)
    http_ua.send_request()
    assert http_ua.response_object.status == 405

def test9():
    # OPTIONS method - Expect 200
    x = ruleset.Input(method="OPTIONS",dest_addr="example.com",version="HTTP/1.0",headers={})
    http_ua = http.HttpUA(x)
    http_ua.send_request()
    assert http_ua.response_object.status == 200

def test10():
    # HEAD method - Expect 200
    x = ruleset.Input(method="HEAD",dest_addr="example.com",version="HTTP/1.0",headers={})
    http_ua = http.HttpUA(x)
    http_ua.send_request()
    assert http_ua.response_object.status == 200

def test11():
    # POST method no data - Expect 411
    x = ruleset.Input(method="POST",dest_addr="example.com",version="HTTP/1.0",headers={})
    http_ua = http.HttpUA(x)
    http_ua.send_request()
    assert http_ua.response_object.status == 411

def test12():
    # POST method no data with content length header - Expect 200
    x = ruleset.Input(method="POST",dest_addr="example.com",version="HTTP/1.0",headers={"Content-Length":"0"},data="")
    http_ua = http.HttpUA(x)
    http_ua.send_request()
    assert http_ua.response_object.status == 200

