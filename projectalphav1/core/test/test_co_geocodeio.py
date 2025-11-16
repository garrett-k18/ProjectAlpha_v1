from geocodio import Geocodio
import requests

# Test with direct HTTP request to see status codes
def test_http_direct():
    print("=== Direct HTTP Test ===")
    url = "https://api.geocod.io/v1.9/geocode"
    params = {
        'q': '1600 Vine St, Los Angeles, CA 90028',
        'fields': 'census',
        'api_key': 'd18926666611a9e42616c8aa8418e698b4126e8'
    }
    
    try:
        response = requests.get(url, params=params)
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("Success! Response received")
            fields = data['results'][0]['fields']
            print(f"Census field: {fields.get('census', 'NOT_PRESENT')}")
        elif response.status_code == 403:
            print("403 Forbidden - Invalid API key or insufficient permissions")
            print(f"Response: {response.text}")
        elif response.status_code == 422:
            print("422 Unprocessable Entity - Client error")
            print(f"Response: {response.text}")
        elif response.status_code == 429:
            print("429 Too Many Requests - Rate limit exceeded")
            print(f"Response: {response.text}")
        elif response.status_code == 500:
            print("500 Server Error - Geocodio internal error")
            print(f"Response: {response.text}")
        else:
            print(f"Unexpected status code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Exception occurred: {e}")

# Test with Python client
def test_python_client():
    print("\n=== Python Client Test ===")
    try:
        client = Geocodio("d18926666611a9e42616c8aa8418e698b4126e8")
        address = "1600 Vine St, Los Angeles, CA 90028"
        response = client.geocode(address, fields=["census"])
        print("Python client succeeded")
        print(f"Census field: {response.results[0].fields.census}")
    except Exception as e:
        print(f"Python client exception: {e}")

if __name__ == "__main__":
    test_http_direct()
    test_python_client()
