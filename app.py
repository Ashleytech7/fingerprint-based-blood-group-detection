from flask import Flask, request, jsonify, render_template
import numpy as np
import tensorflow as tf
import cv2
import os
import ssl
from werkzeug.utils import secure_filename
from tensorflow.keras.preprocessing.image import load_img, img_to_array

# Disable SSL verification if needed
ssl._create_default_https_context = ssl._create_unverified_context

app = Flask(__name__)

# Load the pre-trained model
MODEL_PATH = './model/model.h5'
if os.path.exists(MODEL_PATH):
    model = tf.keras.models.load_model(MODEL_PATH)
else:
    raise FileNotFoundError("Model file not found. Ensure the model exists in the correct path.")

# Define allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp'}

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to preprocess images
def preprocess_image(file_path):
    img = load_img(file_path, target_size=(64, 64))  # Resize image to match model input
    img_array = img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    return img_array

@app.route('/')
def home():
    return render_template('index.html')  # Load the homepage

@app.route('/upload')
def upload():
    return render_template('form.html')  # Ensure you have 'form.html' in templates


@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Allowed types: png, jpg, jpeg, bmp'}), 400
    
    # Save the uploaded file
    filename = secure_filename(file.filename)
    file_path = os.path.join('uploads', filename)
    os.makedirs('uploads', exist_ok=True)  # Ensure uploads directory exists
    file.save(file_path)

    try:
        # Preprocess the image
        img = preprocess_image(file_path)
        
        # Make prediction
        predictions = model.predict(img)
        if predictions.size == 0:
            raise ValueError("Model did not return valid predictions")
        
        predicted_class = int(np.argmax(predictions[0]))
        class_names = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        predicted_label = class_names[predicted_class]

        return jsonify({
            'predicted_class': predicted_class,
            'predicted_label': predicted_label,
            'confidence': float(np.max(predictions[0]))
        })

    except Exception as e:
        return jsonify({'error': f"Prediction failed: {str(e)}"}), 500
    
    finally:
        # Clean up saved file
        if os.path.exists(file_path):
            os.remove(file_path)

if __name__ == '__main__':
    app.run(debug=True)