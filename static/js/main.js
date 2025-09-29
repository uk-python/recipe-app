const searchResult = document.getElementById('search-results-container'); // 検索結果表示エリアを取得（OK）
const searchNameForm = document.getElementById("search-name-form"); // レシピ名検索フォーム取得
const searchIngredientsForm = document.getElementById("search-ingredients-form"); // 材料検索フォーム取得
const searchNameButton = searchNameForm.querySelector('button[type="submit"]'); // レシピ名検索ボタン取得
const searchIngredientsButton = searchIngredientsForm.querySelector('button[type="submit"]'); // 材料検索ボタン取得
let currentRecipes = []; // 現在表示されているレシピの配列
// レシピ名検索フォームの送信イベント
searchNameForm.addEventListener("submit", function (event) {
  event.preventDefault(); // フォームのデフォルト送信をキャンセル
  (searchNameButton.disabled = true); // 連打防止のためボタンを無効化
  const searchNameInput = document.getElementById("search-name-input");
  const inputName = searchNameInput.value;
  if (!inputName || inputName.trim() === "") {
    return alert("検索ワードを入力してください");
  }
  console.log(inputName);

  fetch("/api/search", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: "query=" + encodeURIComponent(inputName),
  })
    .then(function(response){
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(function(data){
      console.log(data);
      if (data.status === "error"){
        return searchResult.innerHTML = `<p>${data.message}</p>`;
      }
      currentRecipes = data.data;

      // 検索結果をHTMLとして生成
      let htmlContents = '';
      for (let i = 0; i < data.data.length; i++) {
        const recipe = data.data[i];
        htmlContents += `
          <div class="recipe-item">
            <h3><a href="/recipe/${recipe.id}">${recipe.title}</a></h3>
            <img src="${recipe.image_url}" alt="${recipe.title}" />
            <p>${recipe.description}</p>
            <p>調理時間目安: ${recipe.time_min}分</p>
          </div>
        `;
      }
      searchResult.innerHTML = htmlContents; 
      searchNameButton.disabled = false;
    })
    .catch(function(err){
      console.error('fetch error', err)
      searchResult.innerHTML = '<p>通信エラーが発生しました。しばらく時間をおいて再試行してください。</p>';
      searchNameButton.disabled = false;
    });
}); 

// 材料検索フォームの送信イベント
searchIngredientsForm.addEventListener('submit', function(event){
  event.preventDefault();
  (searchIngredientsButton.disabled = true); // 連打防止のためボタンを無効化
  const searchIngredientsInput = document.getElementById("search-ingredients-input");
  const inputIngredients = searchIngredientsInput.value;
  if (!inputIngredients || inputIngredients.trim() === ""){
    return alert("検索ワードを入力してください");
  }
  console.log(inputIngredients);
  const searchTypeSelect = document.getElementById('search-type-select');
  const searchType = searchTypeSelect.value;
  console.log("検索タイプ:", searchType);

  fetch("/api/search_by_ingredients",{
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: "query=" + encodeURIComponent(inputIngredients) + "&search_type=" + encodeURIComponent(searchType),
  })
    .then(function(response){
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(function(data){
      console.log(data);
      if (data.status === "error"){
        return searchResult.innerHTML = `<p>${data.message}</p>`;
      }
      currentRecipes = data.data;

      let htmlContents = '';
      for (let i = 0; i < data.data.length; i++) {
        const recipe = data.data[i];
        htmlContents += `
          <div class="recipe-item">
            <h3><a href="/recipe/${recipe.id}">${recipe.title}</a></h3>
            <img src="${recipe.image_url}" alt="${recipe.title}" />
            <p>${recipe.description}</p>
            <p>調理時間目安: ${recipe.time_min}分</p>
          </div>
        `;
      }
      searchResult.innerHTML = htmlContents; 
      searchIngredientsButton.disabled = false;
    })
    .catch(function(err){
      console.error('fetch error', err)
      searchResult.innerHTML = '<p>通信エラーが発生しました。しばらく時間をおいて再試行してください。</p>';
      searchIngredientsButton.disabled = false;
    });
});

// 検索結果のリンククリックで詳細取得
searchResult.onclick = function(event) { 
   const link = event.target.closest('a');
   if (!link || !searchResult.contains(link))
    return;

  event.preventDefault();
   const href = link.getAttribute('href');
   const recipeID = href.split('/').pop();

  fetch(`/api/recipes/${recipeID}`, {
    method: "GET",
   })
     .then(function(response){
       return response.json();
     })
     .then(function(data){
      console.log(data);
      const recipe = data.data;
      const originalIngredients = recipe.ingredients.slice(); // 元の材料リストを保存
      let detailHtml = `
      <div class="recipe-detail">
        <div class="left">
          <h1>${recipe.title}</h1>
          <img src="${recipe.image_url}" alt="${recipe.title}" />
          <p>${recipe.description}</p>
          <p class="time">調理時間目安: ${recipe.time_min}分</p>
        </div>
        <div class="right">
          <h2>材料:</h2>
          <ul>
          ${recipe.ingredients.map(ing => `<li>${ing}</li>`).join('')}
          </ul>
          <h2>作り方:</h2>
          <ol>
          ${recipe.steps.map(step => `<li>${step}</li>`).join('')}
          </ol>
         </div>
     </div>
     `;
      searchResult.innerHTML = detailHtml;
      /*const servingsRange = document.getElementById("servings");
      const servingsSlider = document.getElementById("servings-slider");
      servingsSlider.addEventListener("input", function() {
      const servings = servingsSlider.value;
        servingsRange.innerHTML = servings; // スライダーの値を表示
        const newIngredients = [];
        originalIngredients.array.forEach(ingredient)
　　　　});*/

    })
    .catch(function(err){
      console.error('fetch error', err)
      searchResult.innerHTML = '<p>通信エラーが発生しました。しばらく時間をおいて再試行してください。</p>';
      searchNameButton.disabled = false;
          });
      } 
  
// 並び替えセレクトボックスの変更イベント
const sortSelect = document.getElementById('sort-select');
if (sortSelect) {
  sortSelect.addEventListener('change', function() {
    const selectedOption = sortSelect.value;
    let sortedRecipes = [];
    if (selectedOption === 'time_asc'){
       sortedRecipes = currentRecipes.slice().sort(function( a , b ){
        return a.time_min - b.time_min;
      });
    } else if (selectedOption === 'default'){
      sortedRecipes = currentRecipes;
    }
      let htmlContents = '';
      for (let i=0; i < sortedRecipes.length; i++){
        const recipe = sortedRecipes[i];
        htmlContents += `
          <div class="recipe-item">
            <h3><a href="/recipe/${recipe.id}">${recipe.title}</a></h3> 
            <img src="${recipe.image_url}" alt="${recipe.title}" />
            <p>${recipe.description}</p>
            <p>調理時間目安: ${recipe.time_min}分</p>
          </div>
        `;
      }
      searchResult.innerHTML = htmlContents;
      return; 
    });
}

