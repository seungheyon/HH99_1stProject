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

@app.route("/surching", methods=["POST"])
def surching_post():
    url_receive = request.form['url_give']
    comment_receive = request.form['comment_give']
    star_receive = request.form['star_give']

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url_receive, headers=headers)

    soup = BeautifulSoup(data.text, 'html.parser')

    ogimage = soup.select_one('meta[property="og:image"]')['content']
    ogtitle = soup.select_one('meta[property="og:title"]')['content']


    doc = {
	    'title':ogtitle,
	    'star':star_receive,
		'image':ogimage,
		'url': url_receive,
        'comment':comment_receive
    }

    db.mini.insert_one(doc)

    return jsonify({'msg':'저장완료!'})


@app.route("/surching", methods=["GET"])
def surching_get():
	all_comments = list(db.mini.find({},{'_id':False}))
	return jsonify({'result':all_comments})

#로그인 했을 때 글 작성한 사람과 수정하려는 사람이 같을 때만 수정 가능
@app.route("/edit/<idx>", methods=["GET", "POST"])
def board_edit(idx):
    board = mongo.db.board
    data = board.find_one({"_id": ObjectId(idx)}) 
    if request.method == "GET":
        if data is None:
            flash("해당 게시물이 존재하지 않습니다.")
            return redirect(url_for("lists"))
        else:
            if session.get("id") == data.get("writer_id"):
                return render_template("edit.html", data=data)
            else:
                flash("글 수정 권한이 없습니다.")
                return redirect(url_for("board_list"))
    else:
        title = request.form.get("title")
        contents = request.form.get("contents")
        # 또 한번 더 확인,
        if session.get("id") == data.get('writer_id'):
            board.update_one({"_id": ObjectId(idx)}, {
                "$set": {
                    "title": title,
                    "contents": contents,
                }
            })
            flash("수정되었습니다.")
            return redirect(url_for("board_view", idx=idx))
        else:
            flash("글 수정 권한이 없습니다.")
            return redirect(url_for("board_list"))
        

#삭제 기능        
@app.route("/delete/<idx>")
def board_delete(idx):
    board = mongo.db.board
    data = board.find_one({"_id": ObjectId(idx)})
    if session.get("id") == data.get("writer_id"):
        board.delete_one({"_id": ObjectId(idx)})
        flash("삭제 되었습니다.")
    else:
        flash("삭제 권한이 없습니다.")
    return redirect(url_for("board_list"))


if __name__ == '__main__':
	app.run('0.0.0.0', port=5000, debug=True)