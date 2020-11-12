# To test all requests
    Run request_test.py
 $ python3 request_test.py
 
 Description of all tests is given below

# To test con-current requests
    Run load_test.py
    It takes no_request as argument 
 $ python3 load_test.py <no_of_requests>
 e.g
 $ python3 load_test.py 100
 
# TEST 1 (Simple Get Request)
    Checks if page is succesfully fetch and the content is same as original file

# TEST 2 (Conditional GET Request With if-modified-since header)
    Sends If-modified-since header and check if response status code is 304

# TEST 3 (Conditional GET Request With If-None-Mathc header)
    Sends If-None-Match header and check if response status code is 304

# TEST 4 (Simple PUT Request)
    Sends put request for image and checks if image is successfully uploaded

# TEST 5 (Conditional PUT Request)
   - First gets the image suppose image1 and saves its e-tag 
   - Then uploads another image suppose image 2 with same name so the representation of image1 on server is change 
    - Then sends a put request for image1 with If-Match header and since the representatino of image1 on server is different than that of client server should respond with 412 (precondition failed)

# TEST 6 (POST Request)
    - Sends POST Request of image
    - Gets the location of image on server from Location header in the response
    - Check if the image on that location is same as that of sent image

# TEST 7 (404 Not Found)
    - Sends GET request for page which is not on the server
    - Checks if server responds with 404 (Not Found)

# TEST 8 (400 Bad Request)
    - Sends Bad Reqeust
    - Checks if server responds with 400 (Bad Request)

# TEST 9 (501 Method Not Implemented)
    - Sends request with method which is not implemented on the server
    - Checks if server responds with 501 (Method Not Implemented)
# TEST 10 (405 Method Not Allowed)
    - Sends PUT request for url for which PUT method is not allowed
    - Checks if server responds with 405 (Method Not Allowed)

# TEST 11 (Range request)
    - Sends range request with header Range
    - Check if server responds with 206 (Partial Content)
    - Also checks if response body contains part of the page which is requested 

# TEST 12 (Conditional Range request)
    - Sends range request with header Range and If-Range
    - If-Range header contains HTTP date
    - checks if server responds with 206 (Partial Content)
    - Also checks if response body contains part of the page which is requested

# TEST 13 (Conditional Range request)
    - Sends range request with header Range and If-Range
    - If-Range header contains E-tag
    - checks if server responds with 206 (Partial Content)
    - Also checks if response body contains part of the page which is requested

# TEST 14 (DELETE request)
    - Sends DELETE request for image
    - checks if image is deleted or not

# TEST 15 (Test for Cookie)
    - Sends GET request without cookie header
    - Checks if server sends Set-Cookie header

