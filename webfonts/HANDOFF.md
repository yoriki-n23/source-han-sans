# 引き継ぎメモ：Cloudflare Pages での Web フォント配信

最終更新: 2026-09-29

## 目的

源ノ角ゴシック JP（Source Han Sans JP）をソースからビルドして Web フォント化し、Cloudflare Pages で配信する。

## 現在の状態

| 項目 | 状態 |
|---|---|
| ビルド・分割スクリプト | ✅ 完成。PR #1 で `master` にマージ済み（マージコミット `c857d04`） |
| Cloudflare Pages プロジェクト | ✅ `source-han-sans`。Git 連携で作成済み（ユーザーが Claude in Chrome で設定） |
| 初回デプロイ | ✅ Cloudflare Pages のチェックが `c857d04` に「Deploy successful!」を記録（2026-09-27 13:43 UTC） |
| 公開 URL | https://source-han-sans.pages.dev/ （このデプロイ固有の URL: https://ec129bfe.source-han-sans.pages.dev ） |
| 公開ページの中身 | ⚠️ **Claude はまだ見ていない**（下の「環境の制約」参照）。ユーザーの目視確認待ち |
| Cloudflare のビルドログ | ⚠️ 未確認（ビルド時間・警告の有無は不明） |

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
| `webfonts/split.py` | OTF を `unicode-range` 付きの WOFF2 に分割し、`source-han-sans-jp.css` を生成する。分割順は「基本文字・かな → JIS 第1水準 → 第2水準 → その他」で、1 ウェイトあたり 28 ファイル |
| `webfonts/index.html` | デモページ（7 ウェイトの見本と使い方） |
| `webfonts/_headers` | CORS（`*`）と長期キャッシュの設定。フォントのパスに `v2.004` を含めている |
| `webfonts/requirements.txt` | afdko 5.0.1 / fonttools 4.66.0 / brotli 1.2.0 |
| `.github/workflows/cloudflare-pages.yml` | 予備。手動実行のみ。wrangler でデプロイする。使うには `CLOUDFLARE_API_TOKEN` と `CLOUDFLARE_ACCOUNT_ID` の Secrets が必要 |
| `webfonts/README.md` | ユーザー向けの手順書 |

ローカルでのビルドは約 2 分。196 ファイル・合計 25MB で、最大のファイルは約 250KB（Pages の上限は 1 ファイル 25MiB）。Chromium で 7 ウェイトとも表示されることを確認済み。

## 環境の制約（Claude Code クラウドセッション）

- `*.cloudflare.com` と `*.pages.dev` は、ネットワークポリシーで遮断されている（プロキシが 403 を返す。WebFetch も不可）。
  - デプロイ結果は GitHub API で確認できる:
    `curl -s https://api.github.com/repos/yoriki-n23/source-han-sans/commits/master/check-runs`
  - 公開ページを直接見たい場合は、ユーザーが環境設定の Network access に `source-han-sans.pages.dev` を追加する必要がある。
- Claude in Chrome はクラウドセッションからは使えない。ブラウザ操作が必要なときは、ユーザーに Chrome の Claude サイドパネルで操作してもらう。
- PR のマージは、Claude からは自動モードの安全チェックでブロックされた。PR はユーザーがマージする。
- ユーザーは技術的な操作に不慣れ。手順は画面の文言に沿ってクリック単位で示す。トークンなどの秘密情報は、チャットに貼らせない。

## 次にやること（ユーザーが選択済み：1 の公開ページ確認）

2026-09-29 時点で、`master` は `c857d04` のまま変化なし。Cloudflare Pages のチェックも success のまま。

確認手順の案：

1. ネットワーク許可があるか確かめる：`curl -sI https://source-han-sans.pages.dev/`
   - **許可されている場合**：Claude が直接確認する。
     - `curl -sI` で `/`・`/source-han-sans-jp.css`・`/fonts/v2.004/Regular/000.woff2` が 200 を返すか
     - `_headers` の CORS／Cache-Control が効いているか
     - Playwright（`executablePath: '/opt/pw-browsers/chromium'`）でトップページを開いてスクリーンショットを撮る。woff2 の読み込み数と、7 ウェイトが表示されることを確認する
   - **403 の場合**：ユーザーに次のどちらかを頼む。
     - 環境設定の Network access に `source-han-sans.pages.dev` を追加して新しいセッションを始めてもらう
     - ブラウザで URL を開いて、スクリーンショットを貼ってもらう
2. 表示がおかしい場合：Cloudflare ダッシュボード › Workers & Pages › source-han-sans › デプロイ › 最新のデプロイ で、ビルドログを貼ってもらう。
3. 確認が済んだら、この表の「公開ページの中身」の行を更新する。

## 未解決・次の候補

1. **公開ページの確認**：上の「次にやること」を参照。
2. **ライセンス（要判断）**：OFL の予約フォント名 “Source” がある。サブセット化は改変とみなされる可能性がある。広く公開するなら、同じ字形で予約名のない Noto Sans JP のソースへの切り替えか、ファミリー名の変更を検討する。
3. 予備の GitHub Actions ワークフローを残すか削除するか。
4. 任意：独自ドメインの設定、他の言語（SC/TC/HK/KR）の追加、分割を利用頻度順にして読み込み量をさらに減らす。
