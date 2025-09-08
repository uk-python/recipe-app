from flask import Flask  # Flask本体をインポート
from flask import render_template,request, redirect,flash # テンプレート描画・リクエスト取得・JSON返却・リダイレクト・フラッシュメッセージ表示
import json  # JSONファイルを扱うための標準ライブラリ
from flask_sqlalchemy import SQLAlchemy  # SQLAlchemyをインポート
import os  # OS操作を行うための標準ライブラリ
import re  # 正規表現を扱うための標準ライブラリ
BASEDIR = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)  # Flaskアプリケーションのインスタンスを作成
app.secret_key = 'recipe_secret_key'  # セッション管理やフラッシュメッセージ表示に必要な秘密鍵を設定
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASEDIR, 'recipes.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)  # SQLAlchemyのインスタンスを作成

class Recipe(db.Model):  # SQLAlchemyのモデルクラスを定義
    id = db.Column(db.Integer, primary_key=True)  # レシピID（主キー）
    title = db.Column(db.String(80), nullable=False)  # レシピタイトル
    description = db.Column(db.String(500), nullable=False)  # レシピ説明
    image_url = db.Column(db.String(200), nullable=True)  # 画像URL
    ingredients = db.Column(db.PickleType, nullable=False)  # 材料リスト（PickleTypeでリストを保存）
    steps = db.Column(db.PickleType, nullable=False)  # 手順リスト（PickleTypeでリストを保存）
    time_min = db.Column(db.Integer, nullable=True)  # 調理時間（分）   

from sqlalchemy import text

db_path = os.path.join(BASEDIR, 'recipes.db')
print("FLASK_APP FILE :", __file__)
print("CWD           :", os.getcwd())
print("DB PATH       :", db_path)
print("EXISTS BEFORE :", os.path.exists(db_path))

with app.app_context():
    db.create_all()  # データベースのテーブルを作成
    db.session.execute(text("SELECT 1"))  # 強制接続（エラーがあればここで出ます）

print("EXISTS AFTER  :", os.path.exists(db_path))

@app.route('/')  # ルートURL（ホーム）にアクセスしたときの処理
def home():  # ホーム画面の表示処理
     return render_template('index.html', recipes=[])  # 初期表示時はレシピ一覧を表示しない（recipes=[]）・index.htmlテンプレートを描画

@app.route('/search', methods=['POST'])  # /searchにPOSTリクエストが来たときの処理
def search_recipes():  # 検索処理の関数。/searchにPOSTされたときに呼ばれる
    query = request.form.get('query')  # フォームから検索キーワードを取得
    keywords = query.strip().lower().split()  # キーワードを小文字に変換し、前後の空白を削除してリスト化
    filtered_recipes = []  # 検索結果を格納するリスト
    for recipe in recipes:  # 全レシピを1件ずつチェック
        is_all_keywords_recipe = True  # 全キーワードが一致するか判定するフラグ
        for keyword in keywords:  # 入力されたキーワードを1つずつ確認
            if keyword not in recipe['title']  and keyword not in recipe['description']:  # タイトルにも説明にも含まれなければ
                is_all_keywords_recipe = False  # フラグをFalseに
                break  # 1つでも一致しなければ次のレシピへ
        if is_all_keywords_recipe == True:  # 全キーワードが一致した場合
            filtered_recipes.append(recipe)  # 検索結果リストに追加    
    if not filtered_recipes:  # 検索結果が空の場合
        return render_template('index.html', recipes=False, no_results=True)  # 「見つかりませんでした」表示

    return render_template('index.html', recipes=filtered_recipes)  # 検索結果をテンプレートに渡して表示

@app.route('/search_by_ingredients',methods=['POST'])  # /search_by_ingredientsにPOSTリクエストが来たときの処理
def search_by_ingredients():  # 材料検索の関数。/search_by_ingredientsにPOSTされたときに呼ばれる
    query = request.form.get('query')  # フォームから検索キーワード（材料名）を取得
    ingredients = query.strip().lower().split()  # 材料キーワードを小文字に変換し、前後の空白を削除してリスト化
    filtered_ingredients = []  # 検索結果を格納するリスト
    for recipe in recipes:  # 全レシピを1件ずつチェック
        is_all_ingredients_recipe = True  # 全材料キーワードが一致するか判定するフラグ
        for ingredient in ingredients:  # 入力された材料キーワードを1つずつ確認
            is_keyword_found = False  # 材料がレシピに含まれているか判定するフラグ
            for item in recipe['ingredients']:  # レシピの材料リストを1つずつ確認
                item = item.lower().strip()  # 材料名を小文字に変換し、前後の空白を削除
                if ingredient in item:  # 材料キーワードが含まれていれば
                    is_keyword_found = True
                    break
            if not is_keyword_found:  # 材料キーワードが1つでも一致しなければ
                is_all_ingredients_recipe = False
                break
        if is_all_ingredients_recipe:  # 全材料キーワードが一致した場合
            missing_ingredients = []  # 足りない材料を格納するリスト
            for miss_item in recipe['ingredients']:
                miss_item = miss_item.lower().strip()
                if miss_item not in ingredients:
                    missing_ingredients.append(miss_item)
            recipe['missing_ingredients'] = missing_ingredients  # レシピに足りない材料リストを追加
            step_count = len(recipe['steps']) # 手順数を取得
            filtered_ingredients.append((step_count,recipe))   # 手順数とレシピをタプルでリストに追加
    if not filtered_ingredients:  # 検索結果が空の場合
        return render_template('index.html', recipes=[], no_results=True)  # 空リストを渡すことでTypeErrorを防ぐ
    filtered_ingredients = [recipe for step_count,recipe in filtered_ingredients] # 手順数を除いたレシピリストを作成
    filtered_ingredients.sort(key = lambda recipe:len(recipe['steps']) )  # 手順数でソート
    return render_template('index.html', recipes=filtered_ingredients)

def get_recipe(recipe_id):
       get_recipe_id = (recipe_id - 1)
       return recipes[get_recipe_id]
@app.route('/recipe/<int:recipe_id>')  # /recipe/数字 にアクセスしたときの処理
def show_recipe(recipe_id):
    recipe = get_recipe(recipe_id)
    return render_template('recipe_detail.html', recipe=recipe)  # recipe_detail.htmlテンプレートを描画し、レシピデータを渡す

@app.route('/admin/recipes/new',methods=['GET'])  # /admin/recipes/newにGETリクエストが来たときの処理
def new_recipe():
    return render_template('new_recipe.html')  # new_recipe.htmlテンプレートを描画

@app.route('/admin/recipes',methods=['POST'])  # /admin/recipesにPOSTリクエストが来たときの処理
def add_recipe():
    title = request.form.get('title')
    description = request.form.get('description')
    image_url = request.form.get('image_url')
    if not image_url:
        image_url = "#"  # 画像URLが空の場合はデフォルトのURLを設定
    ingredients = request.form.get('ingredients').splitlines()  # 改行で分割してリスト化
    steps = request.form.get('steps').splitlines()  # 改行で分割してリスト化
    time_min = request.form.get('time_min')
    new_id = 0
    for number in recipes:
        if number['id'] > new_id:
            new_id = number['id']
    new_id += 1

    new_recipe = {
        'id': new_id,
        'title': title,
        'description': description,
        'image_url': image_url,
        'ingredients': ingredients,
        'steps': steps,
        'time_min': time_min

    }
    recipes.append(new_recipe)  # 新しいレシピをリストに追加
    with open('data/recipes.json' , 'w' ,) as f:
        json.dump(recipes, f,ensure_ascii=False, indent=4)  # レシピリストをJSONファイルに保存
    flash('新しいレシピが追加されました！')  # フラッシュメッセージを表示
    return redirect('/')  # ホーム画面にリダイレクト

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # データベースのテーブルを作成
        if not Recipe.query.first():
            dummy = Recipe(
                title="ダミーレシピ",
                description="説明",
                image_url="#",
                ingredients=["卵", "牛乳"],
                steps=["混ぜる", "焼く"],
                time_min=10
            )
            db.session.add(dummy)
            db.session.commit()
    app.run(debug=True)

