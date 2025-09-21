# AI Object Detection App

An end to end AI powered application that detects objects in uploaded images using **YOLOv11**.  
This project combines a FastAPI backend, MySQL database, and a Streamlit frontend to create a secure and user-friendly object detection platform.


## Features

# User Management
- User Signup with:
  - Full Name
  - Username
  - Password + Confirm Password
- JWT-based secure Login/Logout

# Object Detection
- Upload images in JPG/PNG format
- YOLOv11 powered detection
- View detected objects (JSON + bounding boxes)
- Adjustable confidence threshold
- Get annotated image with bounding boxes

# Upload History
- Track all uploaded images
- View previous detections and annotated results


| Method | Endpoint       | Description               
 
| POST   | /signup      | Register new user             
| POST   | /login       | Authenticate user             
| POST   | /uploadimage | Upload image & detect objects 
| GET    | /outputimage | Get last annotated image      
| GET    | /history     | Get upload history for user  



# uvicorn backend.main:app --reload

# cd frontend
# streamlit run streamlit_app.py
 




Mukesh Yadav
AI/ML Engineer

