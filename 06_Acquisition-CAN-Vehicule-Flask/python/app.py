from flask import Flask, render_template, jsonify
import threading
import time
from acquisition_du_donee import vehicle_data, read_serial

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def get_data():
    return jsonify(vehicle_data)

if __name__ == '__main__':
    thread = threading.Thread(target=read_serial, daemon=True)
    thread.start()
    app.run(debug=True)