from httprequestparser import parseRequest

def test(expected, actual):
    if len(actual) == len(expected):
        for i in range(len(expected)):
            if expected[i] != actual[i]:
                print("Test Failed")
                print("Expected value: ", expected[i])
                print("Actual value: ", actual[i])
                break
        else:
            print("Test Passed")
    else:
        print("Test Failed")
        print("Expected length of returned array : ", len(expected))
        print("Actual length of returned array : ", len(actual))
        
def main():
    test1 = ["get", "/", "HTTP/1.1", {"host:127.0.0.1", "connection:close"}, None]


    expected = """501
    
    print("-----------Running Test 1 --------------")
    print("For request: ", request1)
    test(expected, actual)


    request2="""GET / HTTP/1.1\r
host: 127.0.0.1\r
connection: close\r
\r
Hello World"""
    expected = ["GET", "/", "HTTP/1.1", {"host":"127.0.0.1", "connection":"close"}, "Hello World"]
    actual = parseRequest(request2)
    
    print("-----------Running Test 2 --------------")
    print("For request: ", request2)
    test(expected, actual)

main()