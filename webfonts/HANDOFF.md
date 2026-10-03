# 引き継ぎメモ：Cloudflare Pages での Web フォント配信

最終更新: 2026-10-03

## 目的

源ノ角ゴシック JP（Source Han Sans JP）をソースからビルドして Web フォント化し、Cloudflare Pages で配信する。OFL の予約フォント名への対応として、配信するフォントは **Kaku Sans JP** という名前に変えている（2026-10-03〜）。

## 現在の状態

| 項目 | 状態 |
|---|---|
| ビルド・分割スクリプト | ✅ 完成。PR #1 で `master` にマージ済み（マージコミット `c857d04`） |
| Cloudflare Pages プロジェクト | ✅ `source-han-sans`。Git 連携で作成済み（ユーザーが Claude in Chrome で設定） |
| 初回デプロイ | ✅ Cloudflare Pages のチェックが `c857d04` に「Deploy successful!」を記録（2026-09-27 13:43 UTC） |
| 公開 URL | https://source-han-sans.pages.dev/ （このデプロイ固有の URL: https://ec129bfe.source-han-sans.pages.dev ） |
| 公開ページの中身 | ✅ 2026-09-29 にユーザーのスクリーンショットで確認。7 ウェイトとも源ノ角ゴシックで描き分けられ、ダークモードも正常。woff2 の読み込み数（必要な分だけか）は未計測 |
| Cloudflare のビルドログ | ⚠️ 未確認（ビルド時間・警告の有無は不明） |
| 名前変更（Kaku Sans JP）と予備 Actions の削除 | 🔄 2026-10-03 にこのブランチへ push。PR を作って `master` にマージすると公開サイトに反映される（マージはユーザーが行う） |

## Cloudflare Pages の設定（Git 連携）

- 本番ブランチ: `master`（push するたびに自動デプロイ）
- ビルドコマンド: `pip install -r webfonts/requirements.txt && webfonts/build.sh`
- 出力ディレクトリ: `dist/site`
- 環境変数: `PYTHON_VERSION=3.12`
- API トークンは使っていない。GitHub の Secrets も未登録。

## ファイル構成

| ファイル | 役割 |
|---|---|
| `webfonts/build.sh` | 7 ウェイト（ExtraLight〜Heavy）の JP サブセット OTF を AFDKO でビルドする（`COMMANDS.txt` と同じコマンド）。その後 `split.py` を実行し、`dist/site` に出力する |
| `webfonts/split.py` | OTF を `unicode-range` 付きの WOFF2 に分割し、`kaku-sans-jp.css` を生成する。分割順は「基本文字・かな → JIS 第1水準 → 第2水準 → その他」で、1 ウェイトあたり 28 ファイル。各 WOFF2 の name テーブルと CFF の名前を `FAMILY`（Kaku Sans JP）に変え、日本語名「源ノ角ゴシック」は削除する。著作権・商標・ライセンスの記録（name ID 0/7/13/14）は残す |
| `webfonts/index.html` | デモページ（7 ウェイトの見本と使い方） |
| `webfonts/_headers` | CORS（`*`）と長期キャッシュの設定。フォントのパスは `fonts/KakuSansJP/v2.004/<ウェイト>/` |
| `webfonts/requirements.txt` | afdko 5.0.1 / fonttools 4.66.0 / brotli 1.2.0 |
| `webfonts/README.md` | ユーザー向けの手順書 |

ローカルでのビルドは約 2 分。196 ファイル・合計 25MB で、最大のファイルは約 250KB（Pages の上限は 1 ファイル 25MiB）。Chromium で 7 ウェイトとも表示されることを確認済み。デモページで実際に読み込まれる WOFF2 は 196 ファイル中 48（2026-10-03、ローカルで計測）。予備の GitHub Actions ワークフロー（wrangler でデプロイ）は 2026-10-03 に削除した。必要になったら `b772eb8` から復元できる。

## 環境の制約（Claude Code クラウドセッション）

- `*.cloudflare.com` と `*.pages.dev` は、ネットワークポリシーで遮断されている（プロキシが 403 を返す。WebFetch も不可）。
  - デプロイ結果は GitHub API で確認できる:
    `curl -s https://api.github.com/repos/yoriki-n23/source-han-sans/commits/master/check-runs`
  - 公開ページを直接見たい場合は、ユーザーが環境設定の Network access に `source-han-sans.pages.dev` を追加する必要がある。
- Claude in Chrome はクラウドセッションからは使えない。ブラウザ操作が必要なときは、ユーザーに Chrome の Claude サイドパネルで操作してもらう。
- PR のマージは、Claude からは自動モードの安全チェックでブロックされた。PR はユーザーがマージする。
- ユーザーは技術的な操作に不慣れ。手順は画面の文言に沿ってクリック単位で示す。トークンなどの秘密情報は、チャットに貼らせない。

## 次にやること

1. このブランチから `master` への PR を作り、ユーザーにマージしてもらう（Claude からのマージはブロックされる）。
2. マージ後、Cloudflare Pages のチェックが「Deploy successful!」になったら、ユーザーに https://source-han-sans.pages.dev/ を開いてもらい、見出しが「Kaku Sans JP」になっていることを確認する。
3. 旧 CSS（`source-han-sans-jp.css`）は配信しなくなる。ほかのサイトで使っている場合は、`kaku-sans-jp.css` と `font-family: "Kaku Sans JP"` に書き換えてもらう。

## 未解決・次の候補

1. ~~公開ページの確認~~ → 完了（2026-09-29）
2. ~~ライセンス~~ → 2026-10-03 に対応。ユーザーから判断を任されたため、ファミリー名を変える方法を選んだ。理由：OFL の FAQ では、サブセット化（フォントデータの変更）をすると「改変版」となり、予約フォント名を使えない。Noto Sans JP に切り替えても字形は同じで、名前の問題が解決するだけなので、名前を変えるほうが変更が少ない。名前の "Kaku Sans JP" は仮の名前で、`split.py` の `FAMILY` と `CSS_FILE` を書き換えれば変更できる。法的な助言ではない。
3. ~~予備の GitHub Actions ワークフロー~~ → 削除した（2026-10-03）。
4. 任意：独自ドメインの設定、他の言語（SC/TC/HK/KR）の追加、分割を利用頻度順にして読み込み量をさらに減らす。
