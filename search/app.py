from secrets import token_urlsafe
from werkzeug.security import generate_password_hash, check_password_hash
import certifi
import ssl

from flask import Flask, make_response, render_template, request, jsonify, redirect, url_for
from flask_jwt_extended import *
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required


import os
import jwt
import datetime

from pymongo import MongoClient
client = MongoClient('mongodb+srv://spreta:test@cluster0.1ypzumi.mongodb.net/?retryWrites=true&w=majority')
db = client.dbsparta

# db -> dbUser 로 회원정보 이름 변경
client2 = MongoClient('mongodb+srv://sparta:test@cluster0.agiqarx.mongodb.net/?retryWrites=true&w=majority',tlsCAFile=certifi.where())
dbUser = client2.user

import requests
from bs4 import BeautifulSoup
import hashlib

app = Flask(__name__)

SECRET_KEY = 'search'

@app.route('/')
def home():
	return render_template('index.html')

@app.route('/sub')
def board():
	return render_template('sub.html')



############################# 사용자 검증 #################################
# 게시글 등록 시 로그인 여부 확인
@app.route('/check_token')
@jwt_required
def check_token():
    return jsonify({'msg': 'Token is valid'})


##########################################################################



@app.route("/search", methods=["POST"])
def surching_post():

    url_receive = request.form['url_give']
    review_receive = request.form['review_give']
    star_receive = request.form['star_give']

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url_receive, headers=headers)

    soup = BeautifulSoup(data.text, 'html.parser')

    ogtitle = soup.select_one('meta[property="og:title"]')['content']
    ogdesc = soup.select_one('meta[property="og:description"]')['content']
    ogimage = soup.select_one('meta[property="og:image"]')['content']


    doc = {
	    'title':ogtitle,
        'desc':ogdesc,
	    'star':star_receive,
		'image':ogimage,
        'review':review_receive
    }

    db.mini.insert_one(doc)

    return jsonify({'msg':'리뷰저장완료!'})


@app.route("/search", methods=["GET"])
def surching_get():
	all_mini = list(db.mini.find({},{'_id':False}))
	return jsonify({'result':all_mini})

######################### 로그인, 회원가입 #################################

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

   result = dbUser.member.find_one({'mail':id_receive,'pw':pwpw_hash})
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
   dbUser.member.insert_one(doc)
   return jsonify({'msg':'가입완료'})

#로그아웃
@app.route('/token/remove', methods=['POST'])
def logout():
   resp = jsonify({'logout': True})
   resp = make_response(redirect('/'))
   unset_jwt_cookies(resp)
   return resp

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

############################ 로그인, 회원가입 끝 ################################





# # 수정
# @app.route("/post_modify/<int:question_id>/", methods=["GET","POST"])
# @login_required# 로그인필요
# def modify(question_id):
#     question = Question.query.get_or_404(question_id)
#     if g.user != question.user:
#         flash('수정권한이 없습니다')# 로그인 사용자와 수정 작성자가 같지 않을 때
#         return redirect(url_for('question.detail', question_id=question_id))
#     if request.method == 'POST':  # POST 요청
#         form = post_modify()
#         if form.validate_on_submit():
#             form.populate_obj(question)
#             question.modify_date = datetime.now()  # 수정일시 저장
#             db.session.commit()
#             return redirect(url_for('question.detail', question_id=question_id))
#     else:  # GET 요청
#         form = post_modify(obj=question)
#     return render_template('question/question_form.html', form=form)

# #삭제
# @app.route('/delete/<int:id>/', methods=['POST'])
# @login_required
# def delete(question_id):
#     question = Question.query.get_or_404(question_id)
#     if g.user != question.user:
#         flash('삭제권한이 없습니다')# 로그인 사용자와 수정 작성자가 같지 않을 때
#         return redirect(url_for('question.detail', question_id=question_id))
#     db.session.delete(question)
#     db.session.commit()
#     return redirect(url_for('question._list'))
	
    

if __name__ == '__main__':
	app.run('0.0.0.0', port=5000, debug=True)