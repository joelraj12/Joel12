#Import the necessary libraries for this file
import requests
from io import BytesIO
from PIL import Image, ImageDraw 
import time
from flask import Flask 
import cv2
import numpy as np
import smtplib
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from Image1 import assess_plant_health

app = Flask(__name__)

#To start the program at a specific time
desired_start_time = datetime.time(16,27)

def time_until_start():
    current_time = datetime.datetime.now().time()
    start_datetime = datetime.datetime.combine(datetime.date.today(), desired_start_time)

    if current_time < desired_start_time:
        return (start_datetime - datetime.datetime.now()).seconds
    else:
        next_day_start_datetime = start_datetime + datetime.timedelta(days=1)
        return (next_day_start_datetime - datetime.datetime.now()).seconds

wait_time = time_until_start()
print(f"Waiting for {wait_time} seconds until the specified time starts.....")
time.sleep(wait_time)
print("Initializing...")
time.sleep(1)
print("Program has started!")


# ESP32-CAM IP address
esp32_cam_ip = "192.168.145.200"

# ESP32-CAM endpoint to capture an image
capture_endpoint = f"http://{esp32_cam_ip}/capture"

def capture_image():
    try:
        # Send an HTTP GET request to capture an image
        response = requests.get(capture_endpoint)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Convert the image data from bytes to an Image object
            image_data = BytesIO(response.content)
            image = Image.open(image_data)
            image.save('New Image.jpg')
            image = cv2.imread('New Image.jpg')

# Convert the image to HSV
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# Define the color range for the foreign object
            lower_color = np.array([30, 40, 40])
            upper_color = np.array([90, 255, 255])
            mask = cv2.inRange(hsv, lower_color, upper_color)

# morphological operations to improve the mask
            kernel = np.ones((5, 5), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

# Find contours in the mask
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
# Loop through the contours and filter objects based on size
            min_object_area = 200
            for contour in contours:
                if cv2.contourArea(contour) > min_object_area:
                        x, y, w, h = cv2.boundingRect(contour)
                        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        print("Object located!")
        else:
            print(f"Failed to capture image. Status code: {response.status_code}")

    except Exception as e:
        print(f"Error capturing image: {str(e)}")
    cv2.imshow("Object Detected!",image)

#Import the color threshold file and execute the file
    with open(r"Image1.py", 'r') as file:
        file = file.read()
        cv2.destroyAllWindows()
        time.sleep(0)


start_time = time.time()

# Trigger to send an email to the user for update
while True:
    from_email = "carbonspiders12@gmail.com"
    to_email = "jjessperaj@gmail.com"
    subject = "Plant update"
    body = "Update on Plant Health captured by ESP32 CAM"
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_username = "carbonspiders12@gmail.com"
    smtp_pass = "ppvn tiit yufl pbna"

    image_path = ("New Image.jpg")

    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with open (image_path, "rb") as image_file:
        image2 = MIMEImage(image_file.read(), name = "New Image.jpg")
        msg.attach(image2)

    try: 
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_pass)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        print("Email sent successfully!")

    except Exception as e:
        print(f"Error sending email: {str(e)}!")

    finally:
        if capture_image() == 0:
            print("Error capturing image, try again!")
        else:
            time.sleep(10)
            capture_image()

    elapsed_time = time.time() - start_time
    if elapsed_time >= 95:
        print("Program has been stopped after 95 seconds of runtime!")
        break

    if __name__ == "__main__":
        capture_image()
        assess_plant_health(image_path)






