from flask import Flask  # Flask本体をインポート
from flask import render_template,request, jsonify  # テンプレート描画・リクエスト取得・JSON返却用
import json  # JSONファイルを扱うための標準ライブラリ

recipe = 'data/recipes.json'  # レシピデータのファイルパスを指定
with open(recipe, 'r', encoding='utf-8') as f:  # レシピファイルをUTF-8で開く
    recipes = json.load(f)  # ファイル内容をPythonのリストや辞書として読み込む

app = Flask(__name__)  # Flaskアプリケーションのインスタンスを作成

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
                if ingredient in item.lower():  # 材料キーワードが含まれていれば
                    is_keyword_found = True
                    break
            if not is_keyword_found:  # 材料キーワードが1つでも一致しなければ
                is_all_ingredients_recipe = False
                break
        if is_all_ingredients_recipe:  # 全材料キーワードが一致した場合
            filtered_ingredients.append(recipe)
    if not filtered_ingredients:  # 検索結果が空の場合
        return render_template('index.html', recipes=[], no_results=True)  # 空リストを渡すことでTypeErrorを防ぐ

    return render_template('index.html', recipes=filtered_ingredients)

def get_recipe(recipe_id):
       get_recipe_id = (recipe_id - 1)
       return recipes[get_recipe_id]
@app.route('/recipe/<int:recipe_id>')  # /recipe/数字 にアクセスしたときの処理
def show_recipe(recipe_id):
    recipe = get_recipe(recipe_id)
    return render_template('recipe_detail.html', recipe=recipe)  # recipe_detail.htmlテンプレートを描画し、レシピデータを渡す
