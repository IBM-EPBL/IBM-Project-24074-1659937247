# -*- coding: utf-8 -*-
import re
import numpy as np
import os
from flask import Flask, app, request, render_template
from tensorflow.keras import models
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.python.ops.gen_array_ops import concat
from tensorflow.keras.applications.inception_v3 import preprocess_input
import requests
from flask import Flask, request, render_template, redirect, url_for 
from cloudant.client import  Cloudant
import cv2

client = Cloudant.iam("474aa39b-c16e-47e7-8b7a-21f327c0922d-bluemix","jHLWuxiSfLz7-f6eqB1Nklrc_mtTqDgClxBDjJ7ANkrn",connect=True)
my_database = client.create_database("database-dharma")

app = Flask(__name__)

model1= load_model('Model/body.h5')
model2 = load_model('Model/level.h5')

# default home page
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/index')
def home():
	return render_template('index.html')

#registration page
@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/afterregister',methods=['POST'])
def afterreg():
    if request.method == 'POST':
        x = [x for x in request.form.values()]
        print(x)
        data = {
            '_id': x[1],
            'name': x[0],
            'psw': x[2]
        }
        print(data)
        query = {'_id': {'Seq': data['_id']}}
        docs = my_database.get_query_result(query)
        print(docs)
        print(len(docs.all()))
        if (len(docs.all()) == 0):
            url = my_database.create_document(data)
            return render_template('register.html', data="Register, please login using your details")
        else:
            return render_template('register.html', data="You are already a member, please login using your details")

@app.route('/login')
def login():
	return render_template('login.html')

@app.route('/afterlogin', methods=['GET', 'POST'])
def afterlogin():
        if request.method == 'POST':
            user = request.form['_id']
            passw = request.form['psw']
            print(user, passw)

            query = {'_id': {'$eq': user}}
            docs = my_database.get_query_result(query)
            print(docs)
            print(len(docs.all()))
            if (len(docs.all()) == 0):
                return render_template('login.html', pred="The username is not found.")
            else:
                if ((user == docs[0][0]['_id'] and passw == docs[0][0]['psw'])):

                    return render_template("prediction.html")
                else:
                    return render_template('login.html',data="user name and password incorrect")
 
@app.route('/logout')
def logout():
    return render_template('logout.html')

@app.route('/prediction')
def prediction():
    return render_template('prediction.html')  
    
@app.route('/result', methods=["GET", "POST"]) 
def res():
    if request.method=="POST":
        f=request.files['fileupload']
        basepath=os.path.dirname(__file__) #getting the current path i.e where app.py is present
        print("current path", basepath) 
        filepath=os.path.join(basepath, 'uploads', f.filename) #from anywhere in the system we can give image t
        print("upload folder is", filepath)
        f.save(filepath)
        import warnings
        warnings.filterwarnings('ignore')
        img=image.load_img(filepath, target_size=(224,224))
        x=image.img_to_array(img)#img to array 
        x=np.expand_dims (x, axis=0) #used for adding one more dimension 
      #  print(x)
        img_data=preprocess_input(x) 
        prediction1=np.argmax(model1.predict(img_data)) 
        prediction2=np.argmax(model2.predict(img_data))
        #prediction=model.predict(x) 
        #instead of predict_classes(x) we can use predict(X) ---->predict_classes #print("prediction is ", prediction)
        index1=['front', 'rear', 'side']
        index2=['minor', 'moderate', 'severe']
        #result = str(index[output[0]])
        result1 = index1 [prediction1]
        result2 = index2[prediction2]
        print(result1)
        print(result2)
        if(result1== "front" and result2 == "minor"):
            value = "3000 - 5000 INR"
        elif(result1 == "front" and result2 == "moderate"):
            value="6000 8000 INR" 
        elif(result1=="front" and result2 == "severe"):
            value="9000 11000 INR" 
        elif(result1 == "rear" and result2 == "minor"):
            value="4000 - 6000 INR"
        elif(result1 == "rear" and result2 == "moderate"):
            value="7000 9000 INR" 
        elif(result1 == "rear" and result2 == "severe"):
            value="11000 - 13000 INR"
        elif(result1 == "side" and result2 == "minor"):
            value = "6000 - 8000 INR" 
        elif(result1 == "side" and result2 == "moderate"):
            value="9000 - 11000 INR" 
        elif(result1 == "side" and result2 == "severe"):
            value = "12000 - 15000 INR"
        else:
            value="16000 - 50000 INR"
        return render_template('prediction.html', prediction = result1+" "+result2+" "+value)

if __name__ =='__main__':
	app.debug = True
	app.run(debug = True, use_reloader=True)