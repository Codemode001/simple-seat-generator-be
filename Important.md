# FastAPI Seat Layout Detection Backend
### This backend processes uploaded seat layout images, detects seat positions, and generates a Next.js frontend script.

### Setup Instructions
1. Create & Activate a Virtual Environment
* On macOS/Linux: * 

```python3 -m venv venv
source venv/bin/activate
```

* On windows *

```python -m venv venv
venv\Scripts\activate
```

2. Install Dependencies

```python pip install -r requirements.txt
```

3. Run the FastAPI Server

For local development:

```python uvicorn main:app --reload
```

For deployment (accessible on the network):

```python uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```


### API Endpoint
- POST /upload-seat-layout
    - Description: Accepts an image upload, detects seats, and returns a Next.js frontend script.
    - Request:
        - image: Seat layout image file (multipart/form-data)
    - Response:

    ```json {
         "script": "Generated Next.js script..."
        }

    ```
