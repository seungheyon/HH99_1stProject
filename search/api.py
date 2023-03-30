# import json
# from operator import contains
# import re
from secrets import token_urlsafe
# from typing import Container
# from unittest import result
# from xml.dom.minidom import Document
# import click
# from importlib_metadata import method_cache
from pymongo import MongoClient
# from bson.json_util import dumps
from werkzeug.security import generate_password_hash, check_password_hash
import certifi
import ssl
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_jwt_extended import *
import os
import jwt
import datetime
from bs4 import BeautifulSoup
import hashlib


app = Flask(__name__)


client = MongoClient('mongodb+srv://sparta:test@cluster0.agiqarx.mongodb.net/?retryWrites=true&w=majority',tlsCAFile=certifi.where())
db = client.user

SECRET_KEY = 'search'

@app.route('/')
def home():
   return render_template('./index.html')

# 로그인 화면 이동
@app.route("/login")
def loginWindow():
   return render_template('login.html')
# 로그인
@app.route('/signin', methods=["POST"])
def login():
   id_receive = request.form['id_give']
   pwpw_receive = request.form['pwpw_give']   
   pwpw_hash = hashlib.sha256(pwpw_receive.encode('utf-8')).hexdigest()
   print(id_receive, pwpw_receive, pwpw_hash)

   result = db.member.find_one({'mail':id_receive,'pw':pwpw_hash})
   print("result[name] : ",result['name'])
   if result['name'] is not '':
      payload = {
         'id' : id_receive,
         'exp' : datetime.datetime.utcnow() + datetime.timedelta(seconds=60*60*24)
      }
      token = jwt.encode(payload,SECRET_KEY,algorithm='HS256')
      print("token : ", token)

      return jsonify({'result' : 'success', 'token':token})
   else:
      return jsonify({'result':'fail', 'msg':'아이디/비밀번호가 일치하지 않습니다.'})

@app.route('/isVal',methods=['GET'])
def api_valid():
   token_receive = request.cookies.get('mytoken')
   try:
      payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
      userinfo = db.member.find_one({'mail' : payload['id']}, {'_id':0})
      return jsonify({'result':'success', 'nickname':userinfo['nick']})
   except jwt.ExpiredSignatureError:
      return jsonify({'result':'fail', 'msg':'로그인 시간 만료'})
   except jwt.exceptions.DecodeError:
      return jsonify({'result':'fail','msg':'로그인 정보 없음'})

#     ## *** find_one 시에 아무것도 없을 때의 데이터 형태 알아야함 ***
#     user = db.articles.find_one( {'user_id' : user_id},{'user_pwd' : user_pw})
#     if user is None:
#         return jsonify({'login' : False})


#     access_token = create_access_token(identity = user_id, expires_delta = False)
#     refresh_token = create_refresh_token(identity = user_id)

#     resp = jsonify({'login' : True})

#     # 서버에 저장
#     set_access_cookies(resp, access_token)
#     set_refresh_cookies(resp, refresh_token)

#     print(access_token)
#     print(refresh_token)
#     return resp, 200

# 회원가입
@app.route('/signup', methods=["POST"])
def register():
   name_receive = request.form['name_give']
   mail_receive = request.form['mail_give']
   pw_receive = request.form['pw_give']
   pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
   doc ={
      'name' : name_receive,
      'mail' : mail_receive,
      'pw' : pw_hash
   }
   db.member.insert_one(doc)
   return jsonify({'msg':'가입완료'})

   

# JWT 매니저 활성화
app.config.update(DEBUG = True, JWT_SECRET_KEY = "thisissecertkey" )
# 정보를 줄 수 있는 과정도 필요함 == 토큰에서 유저 정보를 받음

# jwt = JWTManager(app)

# # JWT 쿠키 저장
app.config['JWT_COOKIE_SECURE'] = False # https를 통해서만 cookie가 갈 수 있는지 (production 에선 True)
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_ACCESS_COOKIE_PATH'] = '/' # access cookie를 보관할 url (Frontend 기준)
app.config['JWT_REFRESH_COOKIE_PATH'] = '/' # refresh cookie를 보관할 url (Frontend 기준)
# # CSRF 토큰 역시 생성해서 쿠키에 저장할지
# # (이 경우엔 프론트에서 접근해야하기 때문에 httponly가 아님)
app.config['JWT_COOKIE_CSRF_PROTECT'] = True







# 로그아웃
# @app.route('/token/remove', methods=['POST'])
# def logout():
#     # resp = jsonify({'logout': True})
#     resp = make_response(redirect('/'))
#     unset_jwt_cookies(resp)
#     return resp

if __name__ == '__main__':  
   app.run('0.0.0.0',port=5000,debug=True)

