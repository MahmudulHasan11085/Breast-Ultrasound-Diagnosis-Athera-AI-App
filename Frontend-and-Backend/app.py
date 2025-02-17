from flask import Flask, request, jsonify,render_template
import os
from werkzeug.utils import secure_filename
import numpy as np
from PIL import Image
import random
import string
from flask import url_for
from flask import send_from_directory
from generate_report import PatientReport
app = Flask(__name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
print(f"UPLOAD_FOLDER is set to: {UPLOAD_FOLDER}")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def generate_random_filename(length=4):
    return ''.join(random.choices(string.digits, k=length)) + '.png'

@app.route('/chat', methods=['POST'])
def chat():
    message = request.form.get('message')
    
    if 'image' in request.files:
        image = request.files['image']
        
        # If no image is provided, respond with an error
        if image.filename == '':
            return jsonify({'status': 'error', 'message': 'No selected file'}), 400
        
        # Check the MIME type of the uploaded file
        mime_type = image.content_type
        print(f"Received image with MIME type: {mime_type}")
        
        # Process based on the MIME type
        if mime_type.startswith('image/'):
            print(f"Image file type detected: {mime_type}")
            
            # Open the image using Pillow
            try:
                img = Image.open(image)
                print(f"Image opened successfully")
                img = img.convert('RGB')  # Convert to RGB mode if not already in RGB

                # Convert the image to a NumPy array
                img_array = np.array(img)
                patient_id = generate_random_filename(length=10)
                new_filename = message + "_"+ patient_id
                
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
                
                # Save the image with the new random filename
                img.save(image_path)
    
                # Generate image URL
                image_url = url_for('uploaded_file', filename=new_filename, _external=True)
                
                report = PatientReport(patient_name=message, patient_id=patient_id, image1 = image_path, image2 = image_path, age="nil", gender="nil")
                report.generate_report()


                return jsonify({
                    'response': f"Patient Name: {message}\n Prediction: None",
                    'image': image_url  # Return the full image URL
                }), 200

            except Exception as e:
                print(f"Error processing image: {e}")
                return jsonify({
                    'response': f"Error: Processing failed. Check the file if it is corrupted or not. Then Upload the file again with this format: {ALLOWED_EXTENSIONS}",
                    'image': None
                }), 500 
        else:
            return jsonify({
                    'response': f"Error: Please, input a valid ultrasound image with this format: {ALLOWED_EXTENSIONS}",
                    'image': None
                }), 400
            

           
    else:
        print("No image received")
        return jsonify({
                    'response': f"No image file found",
                    'image': None
                }), 400
        
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    # Ensure the upload folder exists
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    
    app.run(debug=True)
