from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

from pymongo import MongoClient
client = MongoClient('mongodb+srv://spreta:test@cluster0.1ypzumi.mongodb.net/?retryWrites=true&w=majority')
db = client.dbsparta

import requests
from bs4 import BeautifulSoup

@app.route('/')
def home():
	return render_template('index.html')


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