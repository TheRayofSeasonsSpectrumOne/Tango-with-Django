import sys
from googleapiclient.discovery import build
my_api_key = "AIzaSyDXMlrPqmIA9EkljoCx99yRtDvEXVd1VQs"
my_cse_id = "005018503204327667165:tikurkplhjt"

def main():
    result = google_search(sys.argv)
    print(result)
    return result

def google_search(search_term, **kwargs):
    service = build("customsearch", "v1", developerKey=my_api_key)
    response = service.cse().list(q=search_term, cx=my_cse_id, **kwargs).execute()
    return response

if __name__ == "__main__":
    main()