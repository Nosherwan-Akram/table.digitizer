

import os
import subprocess
import pandas as pd
import numpy as np
from flask import Flask, jsonify, request
from flask_restful import Api, Resource


from werkzeug.utils import secure_filename

UPLOAD_FOLDER = './coordinates'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

api = Api(app)


def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class upload_file(Resource):
	def post(self):
		if 'Image' not in request.files:
			return jsonify({"status":"404"})
		file = request.files['Image']
        # if user does not select file, browser also
        # submit an empty part without filename
		if file.filename == '':
			return jsonify({"status":"301"})
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			return jsonify({"status":"200"})# redirect(url_for('uploaded_file',filename=filename))

class HTR(Resource):
	def post(self):
		process = subprocess.Popen('python3 ./HTR/src/main.py',shell=True)
		ret1 = process.communicate()[0]
		process.wait()
		print("done")

class PTR(Resource):
	def post(self):
		process = subprocess.Popen('python3 ./PTR/src/main.py',shell=True)
		ret = process.communicate()[0]
		process.wait()
		print("done")

class FetchProbs(Resource):
	def get(self):
		probs = []
		recognized = []
		df = pd.read_csv('output.csv')
		for index, row in df.iterrows():
			if row['probabilityHTR'] > row['probabilityPTR']:
				probs.append(row['probabilityHTR'])
				recognized.append(row['recognizedHTR'])
			else:
				probs.append(row['probabilityPTR'])
				recognized.append(row['recognizedPTR'])
		return jsonify({'status':'200','probs':probs,'recognized':recognized})
#stdout=subprocess.PIPE, stderr=subprocess.STDOUT,

api.add_resource(upload_file,'/uploads')
api.add_resource(HTR,'/htr')
api.add_resource(PTR,'/ptr')
api.add_resource(FetchProbs,'/probs')


if __name__ == "__main__":
	app.run(debug=True)