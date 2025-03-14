from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import PlainTextResponse
from PIL import Image
import io
import json
import cv2
import numpy as np
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def detect_seats(image: Image.Image):
    """
    Detect seats in a cinema layout image using OpenCV.
    """
    # Convert PIL image to OpenCV format
    image = np.array(image)
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    # Apply edge detection
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)

    # Find contours (possible seat locations)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    seats = []
    seat_id = 0

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)

        # Filter out noise by checking size (assume seats have reasonable size)
        if 10 < w < 100 and 10 < h < 100:
            seats.append({
                "id": f"seat-{seat_id}",
                "x": x,
                "y": y,
                "width": w,
                "height": h,
                "reserved": False
            })
            seat_id += 1

    return seats

def generate_nextjs_code(seats):
    """
    Generate a Next.js component dynamically based on detected seats.
    """
    seats_json = json.dumps(seats, indent=2)

    nextjs_code = f"""\
import {{ useState }} from 'react';

export default function SeatReservation() {{
  const [seats, setSeats] = useState({seats_json});

  const toggleReservation = (id) => {{
    setSeats(seats.map(seat =>
      seat.id === id ? {{ ...seat, reserved: !seat.reserved }} : seat
    ));
  }};

  return (
    <div style={{ position: 'relative', width: '600px', height: '400px', border: '1px solid black' }}>
      {{seats.map(seat => (
        <button
          key={{seat.id}}
          onClick={{() => toggleReservation(seat.id)}}
          style={{
            position: 'absolute',
            left: seat.x + 'px',
            top: seat.y + 'px',
            width: seat.width + 'px',
            height: seat.height + 'px',
            backgroundColor: seat.reserved ? 'red' : 'green',
            border: '1px solid black'
          }}
        >
          {{seat.id}}
        </button>
      ))}}
    </div>
  );
}}
"""
    return nextjs_code

@app.post("/upload-seat-layout")
async def upload_seat_layout(file: UploadFile = File(...)):
    """
    Process an uploaded seat layout image, detect seats, and generate Next.js code.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")

    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error processing the image.") from e

    # Detect seats from the image
    seats = detect_seats(image)

    if not seats:
        raise HTTPException(status_code=400, detail="No seats detected. Try a clearer image.")

    # Generate Next.js code based on detected seats
    nextjs_code = generate_nextjs_code(seats)
    
    return {"seats": seats}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
