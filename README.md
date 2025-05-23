
修正点その1
can you add the followings?
それぞれのタイトルの右側に
watchlist.htmlに"Go to Index" button
portfolio.htmlに"Do to Index" button
record_w52_high.htmlに"Go to Index button"

修正点その2
by the way can you add a button that can work 4 different way as below?
Plot.htmlに追加するボタン
index.htmlからPlotへいった場合にshows"Go to Index" button
watchlist.html からplotへ行った場合にshows"Go to Watchlist" button
portfolio.htmlからplotへいった場合にshows"Go to Portfolio" button
record_w52_high.htmlからいった場合にshows"Go to Record W53 High" button

t1はここまで出来た

ｔ2では
filtered_reslults テーブルを作成してデータを入力する仕組みは出来た
さらにはfiltered_result.htmlを作成して今までインデックスで表示したいた部分を移した
表示はカラムをフリーズさせてその他をスクロール出来るようにした

それから不思議なんだがこの部分をコメントアウトしているんだが依然として Back to Filtered Results の表示が出てる　普通の Go Back にしたいのだが
        <!-- {% elif source == 'filtered_results' %}
            <a href="{{ url_for('filtered_results') }}" class="button">Back to Filtered Results</a> -->
コメントの形式: Jinja2のテンプレートエンジン（Flaskで使用）の標準的なコメントアウト方法は {# ... #} です
 {# <a href="{{ url_for('filtered_results') }}" class="button">Back to Filtered Results</a> #}

t3では下記が実行できた

Index.htmlのfiltered_resultsからplotへいったときにその時点のテーブルを読み込んで"Previous""Next"ボタンで順次表示させる
watchlist.htmlからplotへいったときにその時点のテーブルを読み込んで"Previous""Next"ボタンで順次表示させる
portfolio.htmからplotへいったときにその時点のテーブルを読み込んで"Previous""Next"ボタンで順次表示させる
record_w52_high.htmからplotへいったときにその時点のテーブルを読み込んで"Previous""Next"ボタンで順次表示させる

watchlist と portfolio を新たに追加する際に seccode 順に並べ替えて保存させるようにした
filterd results と recordW52 は常にコード順で保存されているのでそのまま使える

t3-1では
全てのページをスクロールできるようにした
filtered results テーブルがないときは作るというロジックが正しく実行されるようにした
"Or Enter Sec Code Directly" で index.html から plotへいったときも"Go to Filtered Results" が表示されていたが修正してindexからいったときには
Privious/Nextボタンが表示されず "Go to Index" でindexへ戻れるようにしたつもり
w52 テーブルでデータがないときにはエラーになってしまってNextボタンを使うことが出来ないので読み込むテーブルにデータがなくてもPrivious と Nextボタンが使えるようにした
Or Enter Sec Code Directlyでインデックスから行ったときも企業名が表示されようにした

t3-2では
watchlist.htmlからplotへいったときに表示されている　Add to Watchlist　を　Remove　ボタンに変えた
portfolio.htmからplotへいったときに表示されている　Add to Portfolio　を　Remove　ボタンに変えた
record_w52_high.html から plot へ行ったときに Remove from 52W High を追加した


t3-3では
is_heroku = True として常にHerokuのテーブルを参照するようにしてある
record W52 High Tableのtimestampが2024-12-16 04:01:16.444810+00:00と表示されるので秒単位までにする時間までにするように修正した

ｔ4-2では
フォルダーの構成を変更してapp.pyからwatchlist, portfolio, record_high ルートを外してroutesフォルダーへ移した
project/
├── app.py
├── .env
└── application/
       ├── backend/
       |      ├── __init__.py
       |      ├── auth.py
       |      ├── db_connect.py
       |      ├── engine.py
       |      ├── fetch_company_data.py
       |      ├── filtered_table.py
       |      └── .py
       ├── fonts/
       ├── routes/
       |      ├── __init__.py
       |      ├── portfolio_route.py
       |      ├── record_w52_high_route.py
       |      └── watchlist_route.py
       ├── static/
       |      ├── css/
       |      ├── js/
       |      └── images/
       ├── templates/
       |       ├── filtered_results.html
       |       ├── index.html
       |       ├── login.html
       |       ├── plot.html
       |       ├── portfolio.html
       |       ├── record_w52_high.html
       |       └── watchlist.html
       ├── __init__.py
       ├── plot_fins_all_bps_opvalues.py
       ├── plot_fins_all_netsales.py
       └── stok_price.py

filtered_results テーブルの['earn_flag', 'div_flag']カラムが空になっていたのは、fins_all_netsales テーブルのカラムが'Earn_flag', 'Div_flag'と大文字で始まっていたからだった
カラム名を全て小文字で保存するように修正した
backend フォルダを作って：
       db_connect を de_connect, engineに分割した　そしてengineだけをインポートするように修正した
       auth.py, fetch_company_data.py, filtered_table.py を移動させて参照するようにした
       
       plot_fins_all_bps_opvalues.pyとplot_fins_all_netsales.pyも移動させて参照させたがなぜかプロットページでグラフを表示できなくなったので参照先は今まで通りapplication内のスクリプトにしてある
t4-3 では
Value routeを追加してplotページの調整をした
indexページも修正したがボタンの色をplotページと後で合わせる予定
project/
├── app.py
├── .env
└── application/
       ├── backend/
       |      ├── __init__.py
       |      ├── auth.py
       |      ├── db_connect.py
       |      ├── engine.py
       |      ├── fetch_company_data.py
       |      ├── filtered_table.py
       |      ├── #plot_fins_all_bps_opvalues.py
       |      ├── #plot_fins_all_netsales.py       
       |      └── stock_price.py  #fetch_company_data.pyで呼ばれている
       ├── fonts/
       ├── routes/
       |      ├── __init__.py
       |      ├── portfolio_route.py
       |      ├── record_w52_high_route.py
       |      ├── Value_route.py
       |      └── watchlist_route.py
       ├── static/
       |      ├── css/
       |      ├── js/
       |      └── images/
       ├── templates/
       |       ├── filtered_results.html
       |       ├── index.html
       |       ├── login.html
       |       ├── plot.html
       |       ├── portfolio.html
       |       ├── record_w52_high.html
       |       ├── Value.html
       |       └── watchlist.html
       ├── __init__.py
       ├── plot_fins_all_bps_opvalues.py
       ├── plot_fins_all_netsales.py
       └── .py

plotでw52 highを表示させた際にremoveボタンを追加した
seccode directでplotへ行った場合にcompanyname が 会社名がありませんとなってしまうのを修正した
plotでfiltered_resultsページを表示させたときにearn と div flag を追加した

t4-4 ではテーブルの名前を変更した
portfolio-->recordhigh, watchlist-->growth

t5-1での修正点
ここでは、はっしゃんの基準 bps_eval ではない通常のBPSのライン bps を追加する

       bps_clipped = np.clip(df['bps'], 0, None)  # Clip the BPS values at 0

# New: Add bps_clipped line (highlight with distinct color and style)
       ax1.step(df['quarterenddate'], bps_clipped, label='BPS Clipped Line', color='cyan', linestyle='-.', where='mid', zorder=4)

# 🔥 New: Add Scatter plot for key `bps_clipped` points
       ax1.scatter(df['quarterenddate'], bps_clipped, label='BPS Clipped (Points)', color='cyan', marker='*', s=40, zorder=5)
Applied zorder=5 to ensure the points appear on top for visibility. これは見た目で後で変更できる

# Fill area between bps_eval_clipped and bps_clipped
       ax1.fill_between(df['quarterenddate'], bps_eval_clipped, bps_clipped, color='lightcyan', alpha=0.5, step='mid', label='BPS Fill Area')
If needed, adjust alpha (e.g., alpha=0.1 or alpha=0.2) for the desired transparency effect.

t5-2 ではフィルタリングロジックの強化を目的とする

app_t.py ではアップデートしたスクリプトを記載したが実施何がどのようにアップデートされたのかはよくわかラナイ
t5-1 との使い勝手の違いを見定めてから次へ進む



Heroku へアップロードする前に db_connect.py の is_heroku = "DYNO" in os.environ を選択する

uweb=5
📅 Common resample() Frequencies for Time Series
🕐 Intraday
| Code             | Meaning       |
| ---------------- | ------------- |
| `'T'` or `'min'` | Minutes       |
| `'H'`            | Hourly        |
| `'2H'`           | Every 2 hours |
📆 Daily / Weekly
| Code      | Meaning                                  |
| --------- | ---------------------------------------- |
| `'D'`     | Calendar day                             |
| `'B'`     | Business day (no weekends)               |
| `'W-MON'` | Weekly, ends Monday                      |
| `'W-TUE'` | Weekly, ends Tuesday                     |
| `'W-WED'` | Weekly, ends Wednesday                   |
| `'W-THU'` | Weekly, ends Thursday                    |
| `'W-FRI'` | ✅ Weekly, ends Friday (best for markets) |
| `'W-SUN'` | Weekly, ends Sunday                      |
📅 Monthly / Quarterly / Annual
| Code             | Meaning       |
| ---------------- | ------------- |
| `'MS'`           | Month Start   |
| `'M'` or `'ME'`  | Month End     |
| `'Q'`            | Quarter End   |
| `'QS'`           | Quarter Start |
| `'A'` or `'Y'`   | Year End      |
| `'AS'` or `'YS'` | Year Start    |


Excellent observation — you're right to question how candle_width and candle_linewidth are interpreted visually, because they do not use the same unit scale.

Let’s clarify it:
🧩 Units used in mplfinance / matplotlib:
| Setting            | Meaning                                    | Units                                                  |
| ------------------ | ------------------------------------------ | ------------------------------------------------------ |
| `candle_width`     | Horizontal width of the **rectangle body** | **relative to bar spacing** (not pixels or data scale) |
| `candle_linewidth` | Thickness of lines (body outline + wick)   | **points (pt)** — like font size or stroke width       |

🧠 What you're noticing:
    candle_width = 1.2 → much wider body
    candle_linewidth = 2.5 → slightly thicker lines, but not to the same scale as width
So yes — even though numerically 1.2 and 2.5 sound close:
    The body width is visually dominant
    The line width is interpreted in physical stroke thickness, like pt or pixel thickness

Yes! The type parameter in mplfinance.plot() lets you switch between several chart visual styles beyond candle. These can be great for testing readability, print-friendliness, or lightweight rendering.
✅ Supported type values in mplfinance.plot()
| Type              | Description                                                                         |
| ----------------- | ----------------------------------------------------------------------------------- |
| `'candle'`        | Standard **candlestick** chart (open/close bodies + high/low wicks) ✅ most detailed |
| `'ohlc'`          | **OHLC bar chart** — vertical bar + left/right ticks for open/close                 |
| `'line'`          | Simple **closing price line chart** (1 series)                                      |
| `'renko'`         | Brick-style trend chart (ignores time)                                              |
| `'pnf'`           | Point & figure chart (also ignores time)                                            |
| `'line_on_close'` | Closing price line (alias for `'line'`)                                             |
| `'bars'`          | Classic financial **bar chart** style                                               |

🔍 Tips:
    For 'renko' and 'pnf', data is interpreted differently → best used without resampling
    'line' can be helpful for minimalist or thumbnail views
    'ohlc' and 'bars' are great when space is tight

🔧 Width settings for type='ohlc'
While candle uses update_width_config like:
update_width_config=dict(
    candle_linewidth=0.5,
    candle_width=5.0
)
For ohlc, you can use:
update_width_config=dict(
    ohlc_linewidth=1.5,  # Make OHLC bars thicker
    ohlc_ticksize=3.0    # Extend open/close "ticks" wider
)

✅ Solution: Anchor Zero to the Bottom

You can manually set the Y-axis limits so that zero appears near the bottom, and the vertical range focuses on real data.
🧪 Add this after all your plots (before tight_layout()):
-----------------------------------------------------------------------
# 1. Calculate ymax
ymax = max(
    df['bps'].max(),
    df['bps_eval'].max(),
    (df['bps_eval'] + df['opvalue']).max(),
    df['nextyrfcastfairvalue'].max(),
    df['adjusted_divannual_for_chart'].max() / 0.04,
    df['adjusted_fcastdivannual_for_chart'].max() / 0.04,
    df['fairvalue'].max(),
    stock_data['High'].max()
)

# 2. Set axis limits
ax1.set_ylim(bottom=0, top=ymax * 1.1)

# 3. Check if *any* series is clipped at the bottom
clipped_mask = (
    (df['bps'] < 0) |
    (df['bps_eval'] < 0) |
    ((df['bps_eval'] + df['opvalue']) < 0) |
    (df['nextyrfcastfairvalue'] < 0) |
    (df['fairvalue'] < 0) |
    ((df['adjusted_divannual_for_chart'] / 0.04) < 0) |
    ((df['adjusted_fcastdivannual_for_chart'] / 0.04) < 0)
)

# 4. Annotate if any value was clipped below zero
if clipped_mask.any():
    ax1.text(
        df['quarterenddate'].iloc[-1],
        ymax * 1.05,
        "⚠️ CLIPPED!",
        fontsize=12,
        color='red',
        ha='right',
        va='bottom'
    )


----------------------------------------------------------------------
🔍 現在のロジックの動作まとめ：
✅ ゼロより下（負の値）
    bottom=0 で固定しているので マイナス側は見えません（＝クリップ）
    そのため、どれか1つでも0未満があれば「⚠️ CLIPPED!」と表示されます

✅ ゼロより上（プラス側）
    ymax * 1.1 で 上限に10%の余白を加えているため、
    基本的にすべてのプラス値は表示されます
    プラス側は「切られている可能性はほぼない」という前提で動いています

uweb_5
project/
├── .env
├── .gitignore
├── app.py
├── Procfile
├── README.md
├── requirements.txt
└── application/
       ├── backend/
       |      ├── __init__.py
       |      ├── auth.py
       |      ├── db_connect.py
       |      ├── engine.py
       |      ├── fetch_company_data.py
       |      ├── filtered_table.py     
       |      └── stock_price.py  #fetch_company_data.pyで呼ばれている
       ├── fonts/
       ├── routes/
       |      ├── __init__.py
       |      ├── growth_route.py
       |      ├── record_w52_high_route.py
       |      ├── recordhigh_route.py
       |      └── value_route.py
       ├── static/
       |      ├── css/
       |      ├── js/
       |      └── images/
       ├── templates/
       |       ├── filtered_results.html
       |       ├── growth.html
       |       ├── index.html
       |       ├── login.html
       |       ├── plot.html
       |       ├── record_w52_high.html
       |       ├── recordhigh.html
       |       └── value.html
       ├── __init__.py
       ├── plot_fins_all_bps_opvalues.py
       ├── plot_fins_all_netsales.py
       └── 

✅ Step-by-Step: GitHub → GitLab Push Mirroring
1. Go to Your GitHub Repo → Settings → Secrets and variables → Actions → "New repository secret"

Create a new secret:
    Name: GITLAB_TOKEN
    Value: your GitLab personal access token
2. Create a GitHub Action Workflow
📂 Project folder structure example:
your-project/
├── .github/
│   └── workflows/
│       └── mirror-to-gitlab.yml   ✅ <-- THIS is the GitHub Actions workflow file
├── app.py
├── README.md
├── ...

🔁 .github/workflows/mirror-to-gitlab.yml
Navigate to your project directory:
cd /mnt/c/geekom_python_projects/git_projects/uweb_5
Create the directory and file:
mkdir -p .github/workflows
nano .github/workflows/mirror-to-gitlab.yml
Then paste your YAML workflow content and save it (in nano, press Ctrl+O, Enter, then Ctrl+X).
Add and commit the file:
git add .github/workflows/mirror-to-gitlab.yml
git commit -m "Add GitHub Action to mirror repo to GitLab"
Push the commit to GitHub:
git push origin main

Add a file like this:
# .github/workflows/mirror-to-gitlab.yml
name: Mirror to GitLab

on:
  push:
    branches:
      - main  # Adjust if your main branch is different

jobs:
  mirror:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout GitHub Repo
        uses: actions/checkout@v3
        with:
          fetch-depth: 0  # Fetch the full history

      - name: Push to GitLab
        env:
          GITLAB_TOKEN: ${{ secrets.GITLAB_TOKEN }}
        run: |
          git config --global user.name "GitHub Actions"
          git config --global user.email "actions@github.com"

          git remote add gitlab https://oauth2:${GITLAB_TOKEN}@gitlab.com/ofukushi-group/uweb_5.git

          # Push all branches and tags, but avoid pushing hidden refs
          git push gitlab --force --prune --all
          git push gitlab --force --prune --tags

✅ What to Do:
    Update GITLAB_URL:
    Replace USERNAME/REPO with your GitLab path.
    Add Secret:
    In your GitHub repo, go to Settings → Secrets and variables → Actions → New repository secret:
        Name: GITLAB_TOKEN
        Value: (your GitLab personal access token)
    Commit the file to .github/workflows/mirror-to-gitlab.yml.

🔄 To Trigger It Now:
Make any small change to your repo, for example:
echo "# Trigger mirror" >> README.md
git add README.md
git commit -m "Trigger GitHub to GitLab mirror"
git push origin main
