from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from pymongo import MongoClient
import jwt, datetime, hashlib, requests
from bs4 import BeautifulSoup
from bson.objectid import ObjectId

app = Flask(__name__)

client = MongoClient('localhost', 27017)
# client = MongoClient('AWS 아이디', 27017, username="test", password="test")
db = client.dbsparta_plus_week4

SECRET_KEY = 'mytube'


# 메인페이지 - index.html
@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"id": payload['id']})
        return render_template('index.html', nickname=user_info["nick"])
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


# 메인페이지 카테고리 추가 API
@app.route('/posting', methods=['POST'])
def posting():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"id": payload["id"]})
        category_receive = request.form["category_give"]
        doc = {
            "id": user_info["id"],
            "category": category_receive
        }
        db.posts.insert_one(doc)
        return jsonify({"result": "success", 'msg': '카테고리 추가 성공!'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


# 메인페이지 카테고리 DB에서 가져오기 API
@app.route("/get_category", methods=['GET'])
def get_posts():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        categorys = list(db.posts.find({}).sort("date", -1).limit(20))

        for category in categorys:
            category["_id"] = str(category["_id"])
        return jsonify({"result": "success", "msg": "포스팅을 가져왔습니다.", "all_category": categorys})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

# 첫 페이지 - 로그인 화면
@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)

# 회원가입 페이지
@app.route('/register')
def register():
    return render_template('register.html')


# 회원가입 API
@app.route('/api/register', methods=['POST'])
def api_register():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    nickname_receive = request.form['nickname_give']

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    db.user.insert_one({'id': id_receive, 'pw': pw_hash, 'nick': nickname_receive})

    return jsonify({'result': 'success'})


# 로그인 API
@app.route('/api/login', methods=['POST'])
def api_login():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    result = db.user.find_one({'id': id_receive, 'pw': pw_hash})

    if result is not None:
        payload = {
            'id': id_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token.decode('utf-8')})  # pyJWT 1.7이라면 .decode('utf-8') 추가

    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


# 아이디 중복확인 API
@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    id_receive = request.form['username_give']
    exists = bool(db.user.find_one({"id": id_receive}))
    return jsonify({'result': 'success', 'exists': exists})


# 닉네임 중복확인 API
@app.route('/sign_up/check_dup_nick', methods=['POST'])
def check_dup_nick():
    nick_receive = request.form['usernick_give']
    exists = bool(db.user.find_one({"nick": nick_receive}))
    return jsonify({'result': 'success', 'exists': exists})


# 유저 정보 확인 API
@app.route('/api/nick', methods=['GET'])
def api_valid():
    token_receive = request.cookies.get('mytoken')

    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        print(payload) # payload 확인용

        # 닉네임 보내주기
        userinfo = db.user.find_one({'id': payload['id']}, {'_id': 0})
        return jsonify({'result': 'success', 'nickname': userinfo['nick']})

    except jwt.ExpiredSignatureError:
        return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})

    except jwt.exceptions.DecodeError:
        return jsonify({'result': 'fail', 'msg': '로그인 정보가 존재하지 않습니다.'})

# 채널 페이지로 이동
@app.route('/channel')
def channel_page():
    category = request.args.get("category")
    return render_template('channel.html', category=category)


# 카테고리의 채널 조회
@app.route('/api/channel/list', methods=['GET'])
def channel_list():
    category = request.args.get("category")
    channels = list(db.channel.find({'channel_category': category}))

    for channel in channels:
        channel["_id"] = str(channel["_id"])
    return jsonify({'channels': channels})


# 채널 저장
@app.route('/api/channel/insert', methods=['POST'])
def channel_save():
    url = request.form['url']
    desc = request.form['desc']
    category = request.form['category']

    # 받은 url 으로 스크랩핑
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url, headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')

    ogTitle = soup.select_one('meta[property="og:title"]')['content']
    ogImage = soup.select_one('meta[property="og:image"]')['content']
    # ogSite = soup.select_one('meta[property="og:site_name"]')['content'] : youtube
    ogUrl = soup.select_one('meta[property="og:url"]')['content']

    # DB에 insert
    doc ={'channel_name': ogTitle,
          'channel_image': ogImage,
          'channel_url': ogUrl,
          'channel_category': category,
          'channel_desc': desc}
    print(doc)
    db.channel.insert_one(doc)

    return jsonify({'msg': '채널이 저장되었습니다!'})


# 채널 삭제
@app.route('/api/channel/delete', methods=['POST'])
def channel_delete():
    channel_id = request.form['channel_id']
    # pymongo _id의 타입인 objectId로 변환
    db.channel.delete_one({'_id': ObjectId(channel_id)})

    return jsonify({'msg': '삭제되었습니다!'})


# 채널 수정
@app.route('/api/channel/update', methods=['POST'])
def channel_update():
    channel_id = request.form['channel_id']
    channel_desc = request.form['channel_desc']

    # pymongo _id의 타입인 objectId로 변환
    db.channel.update_one({'_id': ObjectId(channel_id)}, {'$set': {'channel_desc': channel_desc}})

    return jsonify({'msg': '수정되었습니다!'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
