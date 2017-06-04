from ftw import ruleset, http, errors
import pytest
import sys

@pytest.mark.skip(reason='Integration failure, @chaimsanders for more info')
def test_cookies1():
    """Tests accessing a site that sets a cookie and then wants to resend the cookie"""
    http_ua = http.HttpUA()
    x = ruleset.Input(dest_addr="ieee.org",headers={"Host":"ieee.org"})
    http_ua.send_request(x)
    with pytest.raises(KeyError):
        print http_ua.request_object.headers["cookie"]
    assert("set-cookie" in http_ua.response_object.headers.keys())
    cookie_data = http_ua.response_object.headers["set-cookie"]
    cookie_var = cookie_data.split("=")[0]
    x = ruleset.Input(dest_addr="ieee.org",headers={"Host":"ieee.org"})
    http_ua.send_request(x)
    assert(http_ua.request_object.headers["cookie"].split('=')[0] == cookie_var)

def test_cookies2():
    """Test to make sure that we don't override user specified cookies"""
    http_ua = http.HttpUA()
    x = ruleset.Input(dest_addr="ieee.org",headers={"Host":"ieee.org"})
    http_ua.send_request(x)
    x = ruleset.Input(dest_addr="ieee.org",headers={"Host":"ieee.org","cookie":"TS01293935=012f3506234413e6c5cb14e8c0d5bf890fdd02481614b01cd6cd30911c6733e3e6f79e72aa"})    
    http_ua.send_request(x)
    assert('TS01293935=012f3506234413e6c5cb14e8c0d5bf890fdd02481614b01cd6cd30911c6733e3e6f79e72aa' in http_ua.request_object.headers["cookie"])

@pytest.mark.skip(reason='Integration failure, @chaimsanders for more info')
def test_cookies3():
    """Test to make sure we retain cookies when user specified values are provided"""
    http_ua = http.HttpUA()
    x = ruleset.Input(dest_addr="ieee.org",headers={"Host":"ieee.org"})
    http_ua.send_request(x)
    x = ruleset.Input(dest_addr="ieee.org",headers={"Host":"ieee.org","cookie":"TS01293935=012f3506234413e6c5cb14e8c0d5bf890fdd02481614b01cd6cd30911c6733e3e6f79e72aa; XYZ=123"})
    http_ua.send_request(x)
    assert(set([chunk.split('=')[0].strip() for chunk in http_ua.request_object.headers["cookie"].split(';')]) == set(['XYZ', 'TS01293935', 'TS01c9c5e8']))

def test_cookies4():
    """Test to make sure cookies are saved when user-specified cookie is added"""
    http_ua = http.HttpUA()
    x = ruleset.Input(dest_addr="ieee.org",headers={"Host":"ieee.org"})
    http_ua.send_request(x)
    x = ruleset.Input(dest_addr="ieee.org",headers={"Host":"ieee.org","cookie":"XYZ=123"})
    http_ua.send_request(x)
    assert('XYZ' in http_ua.request_object.headers["cookie"])

def test_raw1():
    """Test to make sure a raw request will work with \r\n replacement"""
    x = ruleset.Input(dest_addr="example.com",raw_request="""GET / HTTP/1.1\r\nHost: example.com\r\n\r\n""")
    http_ua = http.HttpUA()
    http_ua.send_request(x)
    assert http_ua.response_object.status == 200    

@pytest.mark.skip(reason='Integration failure, @chaimsanders for more info')
def test_raw2():
    """Test to make sure a raw request will work with actual seperators"""
    x = ruleset.Input(dest_addr="example.com",raw_request="""GET / HTTP/1.1
Host: example.com
    

""")
    http_ua = http.HttpUA()
    http_ua.send_request(x)
    assert http_ua.response_object.status == 200    

def test_both1():
    """Test to make sure that if both encoded and raw are provided there is an error"""
    x = ruleset.Input(dest_addr="example.com", raw_request="""GET / HTTP/1.1\r\nHost: example.com\r\n\r\n""", encoded_request="abc123==")
    http_ua = http.HttpUA()
    with pytest.raises(errors.TestError):
        http_ua.send_request(x)

def test_encoded1():
    """Test to make sure a encode request works"""
    x = ruleset.Input(dest_addr="example.com", encoded_request="R0VUIC8gSFRUUC8xLjFcclxuSG9zdDogZXhhbXBsZS5jb21cclxuXHJcbg==")
    http_ua = http.HttpUA()
    http_ua.send_request(x)
    assert http_ua.response_object.status == 200     
    
def test_error1():
    """Will return mail -- not header should cause error"""
    x = ruleset.Input(dest_addr="Smtp.aol.com",port=25,headers={"Host":"example.com"})
    http_ua = http.HttpUA()
    with pytest.raises(errors.TestError):
        http_ua.send_request(x)

def test_error5():
    """Invalid Header should cause error"""
    http_ua = http.HttpUA()
    with pytest.raises(errors.TestError):
        response = http.HttpResponse("HTTP/1.1 200 OK\r\ntest\r\n", http_ua)


def test_error6():
    """Valid HTTP response should process fine"""
    http_ua = http.HttpUA()
    response = http.HttpResponse("HTTP/1.1 200 OK\r\ntest: hello\r\n", http_ua)
    
def test_error7():
    """Invalid content-type should fail"""
    http_ua = http.HttpUA()
    with pytest.raises(errors.TestError):
        response = http.HttpResponse("HTTP/1.1 200 OK\r\nContent-Encoding: XYZ\r\n", http_ua)

def test_error2():
    """Invalid request should cause timeout"""
    x = ruleset.Input(dest_addr="example.com",port=123,headers={"Host":"example.com"})
    http_ua = http.HttpUA()
    with pytest.raises(errors.TestError):
        http_ua.send_request(x)

def test_error3():
    """Invalid status returned in response line"""
    http_ua = http.HttpUA()
    with pytest.raises(errors.TestError):
        response = http.HttpResponse("HTTP1.1 test OK\r\n", http_ua)

def test_error4():
    """Wrong number of elements returned in response line"""
    with pytest.raises(errors.TestError):
        http_ua = http.HttpUA()
        response = http.HttpResponse("HTTP1.1 OK\r\n", http_ua)

def test1():
    """Typical request specified should be valid"""
    x = ruleset.Input(dest_addr="example.com",headers={"Host":"example.com"})
    http_ua = http.HttpUA()
    http_ua.send_request(x)
    assert http_ua.response_object.status == 200
  
    
def test2():
    """Basic GET without Host on 1.1 - Expect 400"""
    x = ruleset.Input(dest_addr="example.com",headers={})
    http_ua = http.HttpUA()
    http_ua.send_request(x)
    assert http_ua.response_object.status == 400

def test3():    
    """Basic GET without Host on 1.0 - Expect 404 (server is VHosted)"""
    x = ruleset.Input(dest_addr="example.com",version="HTTP/1.0",headers={})
    http_ua = http.HttpUA()
    http_ua.send_request(x)
    assert http_ua.response_object.status == 404

def test4():    
    """Basic GET wit Host on 1.0 - Expect 200"""
    x = ruleset.Input(dest_addr="example.com",version="HTTP/1.0",headers={"Host":"example.com"})
    http_ua = http.HttpUA()
    http_ua.send_request(x)
    assert http_ua.response_object.status == 200

def test5():
    """Basic GET without Host on 0.9 - Expect 505 version not supported"""
    x = ruleset.Input(dest_addr="example.com",version="HTTP/0.9",headers={})
    http_ua = http.HttpUA()
    http_ua.send_request(x)
    assert http_ua.response_object.status == 505
    
def test6():
    """Basic GET without Host with invalid version (request line) - Expect 505 not supported"""
    x = ruleset.Input(dest_addr="example.com",version="HTTP/1.0 x",headers={})
    http_ua = http.HttpUA()
    http_ua.send_request(x)
    assert http_ua.response_object.status == 505

def test7():
    """TEST method which doesn't exist - Expect 501"""
    x = ruleset.Input(method="TEST",dest_addr="example.com",version="HTTP/1.0",headers={})
    http_ua = http.HttpUA()
    http_ua.send_request(x)
    assert http_ua.response_object.status == 501

def test8():
    """PROPFIND method which isn't allowed - Expect 405"""
    x = ruleset.Input(method="PROPFIND",dest_addr="example.com",version="HTTP/1.0",headers={})
    http_ua = http.HttpUA()
    http_ua.send_request(x)
    assert http_ua.response_object.status == 405

def test9():
    """OPTIONS method - Expect 200"""
    x = ruleset.Input(method="OPTIONS",dest_addr="example.com",version="HTTP/1.0",headers={})
    http_ua = http.HttpUA()
    http_ua.send_request(x)
    assert http_ua.response_object.status == 200

def test10():
    """HEAD method - Expect 200"""
    x = ruleset.Input(method="HEAD",dest_addr="example.com",version="HTTP/1.0",headers={"Host":"example.com"})
    http_ua = http.HttpUA()
    http_ua.send_request(x)
    assert http_ua.response_object.status == 200

def test11():
    """POST method no data - Expect 411"""
    x = ruleset.Input(method="POST",dest_addr="example.com",version="HTTP/1.0",headers={})
    http_ua = http.HttpUA()
    http_ua.send_request(x)
    assert http_ua.response_object.status == 411

def test12():
    """POST method no data with content length header - Expect 200"""
    x = ruleset.Input(method="POST",dest_addr="example.com",version="HTTP/1.0",headers={"Content-Length":"0","Host":"example.com"},data="")
    http_ua = http.HttpUA()
    http_ua.send_request(x)
    assert http_ua.response_object.status == 200

def test13():
    """Request https on port 80 (default)"""
    x = ruleset.Input(protocol="https",dest_addr="example.com",headers={"Host":"example.com"})
    http_ua = http.HttpUA()
    with pytest.raises(errors.TestError):
        http_ua.send_request(x)    

def test14():
    """Request https on port 443 should work"""
    x = ruleset.Input(protocol="https",port=443,dest_addr="example.com",headers={"Host":"example.com"})
    http_ua = http.HttpUA()
    http_ua.send_request(x)
    assert http_ua.response_object.status == 200
    
    
def test15():
    """Request with content-type and content-length specified"""
    x = ruleset.Input(method="POST", protocol="http",port=80,dest_addr="example.com",headers={"Content-Type": "application/x-www-form-urlencoded","Host":"example.com","Content-Length":"7"},data="test=hi")
    http_ua = http.HttpUA()
    http_ua.send_request(x)
    assert http_ua.response_object.status == 200    
    
def test16():
    """Post request with content-type but not content-length"""
    x = ruleset.Input(method="POST", protocol="http",port=80,dest_addr="example.com",headers={"Content-Type": "application/x-www-form-urlencoded","Host":"example.com"},data="test=hi")
    http_ua = http.HttpUA()
    http_ua.send_request(x)
    assert http_ua.response_object.status == 200

def test17():
    """Post request with no content-type AND no content-length"""
    x = ruleset.Input(method="POST", protocol="http",port=80,uri="/",dest_addr="example.com",headers={"Host":"example.com"},data="test=hi")
    http_ua = http.HttpUA()
    http_ua.send_request(x)
    assert http_ua.response_object.status == 200
    
def test18():
    """Send a request and check that the space is encoded automagically"""
    x = ruleset.Input(method="POST", protocol="http",port=80,uri="/",dest_addr="example.com",headers={"Host":"example.com"},data="test=hit f&test2=hello")
    http_ua = http.HttpUA()
    http_ua.send_request(x)
    assert http_ua.request_object.data == "test=hit+f&test2=hello"
def test19():
    """Send a raw question mark and test it is encoded automagically"""
    x = ruleset.Input(method="POST", protocol="http",port=80,uri="/",dest_addr="example.com",headers={"Host":"example.com"},data="test=hello?x")
    http_ua = http.HttpUA()
    http_ua.send_request(x)
    assert http_ua.request_object.data == "test=hello%3Fx"
