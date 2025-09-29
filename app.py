from flask import Flask,jsonify  # Flask本体をインポート
from flask import render_template,request, redirect,flash # テンプレート描画・リクエスト取得・JSON返却・リダイレクト・フラッシュメッセージ表示
import json  # JSONファイルを扱うための標準ライブラリ
from flask_sqlalchemy import SQLAlchemy  # SQLAlchemyをインポート
from sqlalchemy import or_, and_  # SQLAlchemyのor_関数とand_関数をインポート
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
    return render_template('index.html', recipes=[])    # index.htmlテンプレートを描画し、 初期表示時はレシピ一覧を表示しない

@app.route('/api/search', methods=['POST'])  # /searchにPOSTリクエストが来たときの処理
def api_search_recipes():  # 検索処理の関数。/searchにPOSTされたときに呼ばれる
    query = request.form.get('query')  # フォームから検索キーワードを取得
    if not query.strip():  # キーワードが空の場合
        return jsonify({"status": "error", "message": "キーワードを入力してください"})
    keywords = query.strip().lower().split()  # キーワードを小文字に変換し、前後の空白を削除してリスト化
    filtered_recipes = Recipe.query # 全レシピを取得するクエリ
    for keyword in keywords:  # 入力されたキーワードを1つずつ確認
        filtered_recipes = filtered_recipes.filter(or_(
          (Recipe.title.like(f'%{keyword}%')),
          (Recipe.description.like(f'%{keyword}%'))
          )) # タイトルまたは説明にキーワードが含まれるレシピを絞り
    recipes_to_show = filtered_recipes.all()  # 絞り込んだ結果を取得
    recipes_dict = []  # レシピ情報を辞書形式で格納するリスト
    for recipe in recipes_to_show:  # 検索結果のレシピを1つずつ処理
        recipes_dict.append({
            'id': recipe.id,
            'title': recipe.title, 
            'description': recipe.description,
            'image_url': recipe.image_url,
            'ingredients': recipe.ingredients,
            'steps': recipe.steps,
            'time_min': recipe.time_min

        })
    if not recipes_to_show:  # 検索結果が空の場合
        return jsonify({"status": "error", "message": "検索結果が見つかりませんでした"})  # 「見つかりませんでした」表示
    return jsonify({"status": "success", "data": recipes_dict, "count": len(recipes_dict)})  # 検索結果をJSON形式で返す

@app.route('/api/search_by_ingredients',methods=['POST'])  # /search_by_ingredientsにPOSTリクエストが来たときの処理
def api_search_by_ingredients():  # 材料検索の関数。/search_by_ingredientsにPOSTされたときに呼ばれる
    search_type = request.form.get('search_type')  # フォームから検索タイプを取得
    query = request.form.get('query')  # フォームから検索キーワード（材料名）を取得
    if not query.strip():  # キーワードが空の場合
        return jsonify({"status": "error", "message": "キーワードを入力してください"})  #
    ingredients = query.strip().lower().split()  # 材料キーワードを小文字に変換し、前後の空白を削除してリスト化
    all_recipes = Recipe.query.all()  # 全レシピを取得
    recipes_to_show = [] # 検索結果を格納するリスト
    for recipe in all_recipes: # 全レシピを1つずつ確認
        recipe_ingredients = [i.lower()for i in recipe.ingredients] # レシピの材料を小文字に変換してリスト化
        if search_type == 'and':  # AND検索の場合
            all_ingredients_found = True # 全ての材料が見つかったかどうかのフラグ
            for ingredient in ingredients: # 入力された材料を1つずつ確認
                ingredient_found = False # 材料が見つかったかどうかのフラグ
                for recipe_ingredient in recipe_ingredients: # レシピの材料を1つずつ確認
                    if ingredient in recipe_ingredient: # 入力された材料がレシピの材料に含まれる場合
                        ingredient_found = True # 材料が見つかったとする
                        break
                if not ingredient_found: # 1つでも材料が見つからなかった場合
                    all_ingredients_found = False # 全ての材料が見つかったフラグをFalseにする
                    break
            if all_ingredients_found: # 全ての材料が見つかった場合
                recipes_to_show.append(recipe) # 検索結果にレシピを追加
        elif search_type == 'or': # OR検索の場合
            or_found = False # 少なくとも1つの材料が見つかったかどうかのフラグ
            for ingredient in ingredients: # 入力された材料を1つずつ確認
                for recipe_ingredient in recipe_ingredients: # レシピの材料を1つずつ確認
                    if ingredient in recipe_ingredient: # 入力された材料がレシピの材料に含まれる場合
                        or_found = True
                        break
                if or_found:
                    break 
            if or_found:
                recipes_to_show.append(recipe) # 検索結果にレシピを追加
    recipes_dict = []  # レシピ情報を辞書形式で格納するリスト
    for recipe in recipes_to_show:
        recipes_dict.append({
            'id': recipe.id,
            'title': recipe.title,
            'description': recipe.description,
            'image_url': recipe.image_url,
            'ingredients': recipe.ingredients,
            'steps': recipe.steps,
            'time_min': recipe.time_min
        })
    if not recipes_to_show:
        return jsonify({"status": "error", "message": "検索結果が見つかりませんでした"})  # 「見つかりませんでした」表示
    return jsonify({"status": "success", "data": recipes_dict, "count": len(recipes_dict)}) # 検索結果をJSON形式で返す

@app.route('/api/recipes/<int:recipe_id>', methods=['GET']) # /recipe/数字 にGETリクエストが来たときの処理
def api_show_recipe(recipe_id): # レシピ詳細画面の表示処理, recipe_idはURLから取得した整数
    recipe = Recipe.query.get(recipe_id) # 指定されたIDのレシピをデータベースから取得
    if not recipe:  # レシピが見つからなかった場合
        return jsonify({"status": "error", "message": "レシピが見つかりませんでした"})
    recipe_dict = {
        'id': recipe.id,
        'title': recipe.title,
        'description': recipe.description,
        'image_url': recipe.image_url,
        'ingredients': recipe.ingredients,
        'steps': recipe.steps,
        'time_min': recipe.time_min
    }
    return jsonify({"status": "success", "data": recipe_dict})  # レシピデータをJSON形式で返す

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
    time_min = request.form.get('time_min') # 分単位の調理時間
    new_recipe = Recipe(  # Recipeモデルのインスタンスを作成
        title=title,
        description=description,
        image_url=image_url,
        ingredients=ingredients,
        steps=steps,
        time_min=time_min
    )
    db.session.add(new_recipe)  # 新しいレコードをセッションに追加
    db.session.commit()  # セッションの変更をデータベースにコミット
    flash('新しいレシピが追加されました！')  # フラッシュメッセージを設定
    return redirect('/')  # ホーム画面にリダイレクト

if __name__ == "__main__":
    with app.app_context():  # アプリケーションコンテキストを作成
        db.create_all()  # データベースのテーブルを作成
    app.run(debug=True)

