from ftw import ruleset, http, errors
import pytest

# Will return mail -- not header should cause error
def test_error1():
    x = ruleset.Input(dest_addr="Smtp.aol.com",port=25,headers={"Host":"example.com"})
    http_ua = http.HttpUA(x)
    with pytest.raises(errors.TestError):
        http_ua.send_request()

# Invalid Header should cause error
def test_error5():
    with pytest.raises(errors.TestError):
        response = http.HttpResponse("HTTP/1.1 200 OK\r\ntest\r\n")

# Valid HTTP response should process fine
def test_error6():
    response = http.HttpResponse("HTTP/1.1 200 OK\r\ntest: hello\r\n")

# Invalid content-type should fail
def test_error7():
    with pytest.raises(errors.TestError):
        response = http.HttpResponse("HTTP/1.1 200 OK\r\nContent-Encoding: XYZ\r\n")

# Invalid request should cause timeout
def test_error2():
    x = ruleset.Input(dest_addr="example.com",port=123,headers={"Host":"example.com"})
    http_ua = http.HttpUA(x)
    with pytest.raises(errors.TestError):
        http_ua.send_request()

# Invalid status returned in response line
def test_error3():
    with pytest.raises(errors.TestError):
        response = http.HttpResponse("HTTP1.1 test OK\r\n")

# Wrong number of elements returned in response line
def test_error4():
    with pytest.raises(errors.TestError):
        response = http.HttpResponse("HTTP1.1 OK\r\n")

def test1():
    x = ruleset.Input(dest_addr="example.com",headers={"Host":"example.com"})
    http_ua = http.HttpUA(x)
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

#@pytest.mark.skip(reason="@TODO")
def test10():
    # HEAD method - Expect 200
    x = ruleset.Input(method="HEAD",dest_addr="example.com",version="HTTP/1.0",headers={"Host":"example.com"})
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
    x = ruleset.Input(method="POST",dest_addr="example.com",version="HTTP/1.0",headers={"Content-Length":"0","Host":"example.com"},data="")
    http_ua = http.HttpUA(x)
    http_ua.send_request()
    assert http_ua.response_object.status == 200

def test13():
    # Request https on port 80 (default)
    x = ruleset.Input(protocol="https",dest_addr="example.com",headers={"Host":"example.com"})
    http_ua = http.HttpUA(x)
    with pytest.raises(errors.TestError):
        http_ua.send_request()    

def test14():
    # Request https on port 443 should work
    x = ruleset.Input(protocol="https",port=443,dest_addr="example.com",headers={"Host":"example.com"})
    http_ua = http.HttpUA(x)
    http_ua.send_request()
    assert http_ua.response_object.status == 200
    
    
def test15():
    # Request with content-type and content-length specified
    x = ruleset.Input(method="POST", protocol="http",port=80,dest_addr="example.com",headers={"Content-Type": "application/x-www-form-urlencoded","Host":"example.com","Content-Length":"7"},data="test=hi")
    http_ua = http.HttpUA(x)
    http_ua.send_request()
    assert http_ua.response_object.status == 200    
    
def test16():
    # Post request with content-type but not content-length
    x = ruleset.Input(method="POST", protocol="http",port=80,dest_addr="example.com",headers={"Content-Type": "application/x-www-form-urlencoded","Host":"example.com"},data="test=hi")
    http_ua = http.HttpUA(x)
    http_ua.send_request()
    assert http_ua.response_object.status == 200

def test17():
    # # Post request with no content-type AND no content-length
    x = ruleset.Input(method="POST", protocol="http",port=80,uri="/",dest_addr="example.com",headers={"Host":"example.com"},data="test=hi")
    http_ua = http.HttpUA(x)
    http_ua.send_request()
    assert http_ua.response_object.status == 200
    
def test18():
    # Send a request and check that the space is encoded automagically
    x = ruleset.Input(method="POST", protocol="http",port=80,uri="/",dest_addr="example.com",headers={"Host":"example.com"},data="test=hit f&test2=hello")
    http_ua = http.HttpUA(x)
    http_ua.send_request()
    assert http_ua.request_object.data == "test=hit+f&test2=hello"
def test19():
    # Send a raw question mark and test it is encoded automagically
    x = ruleset.Input(method="POST", protocol="http",port=80,uri="/",dest_addr="example.com",headers={"Host":"example.com"},data="test=hello?x")
    http_ua = http.HttpUA(x)
    http_ua.send_request()
    assert http_ua.request_object.data == "test=hello%3Fx"
