# 源ノ角ゴシック JP Webフォント（Cloudflare Pages 配信）

`cidfont.ps.JP` から日本語サブセット OTF（7ウェイト）をビルドし、`unicode-range` で分割した WOFF2 と CSS を Cloudflare Pages へデプロイします。

- 分割順：基本文字・かな → JIS 第1水準漢字 → 第2水準 → その他（1ウェイト28ファイル、最大でも約250KB）
- ページ上の文字に必要なファイルだけがブラウザに読み込まれます
- 全ファイルが Pages の 1ファイル 25 MiB 上限を大きく下回るため、R2 は不要です

## ローカルでビルド

```sh
pip install -r webfonts/requirements.txt
webfonts/build.sh                  # dist/site に出力（約2分）
WEIGHTS="Regular Bold" webfonts/build.sh   # ウェイトを絞る場合
python3 -m http.server -d dist/site        # http://localhost:8000 で確認
```

## Cloudflare Pages へのデプロイ（GitHub Actions）

1. Cloudflare ダッシュボードで API トークンを作成（テンプレートなしのカスタムトークンで、権限は **Account › Cloudflare Pages › Edit** のみ）
2. GitHub リポジトリの Settings › Secrets and variables › Actions に登録
   - `CLOUDFLARE_API_TOKEN`
   - `CLOUDFLARE_ACCOUNT_ID`（ダッシュボード右側の「Account ID」）
3. `master` に push、または Actions タブから「Deploy web fonts to Cloudflare Pages」を手動実行

初回実行時に Pages プロジェクト `source-han-sans` が自動作成され、`https://source-han-sans.pages.dev/` で公開されます。シークレットが未設定の場合、デプロイはスキップされます（ビルドだけ実行されます）。

## 使い方

```html
<link rel="stylesheet" href="https://source-han-sans.pages.dev/source-han-sans-jp.css">
<style>body { font-family: "Source Han Sans JP", sans-serif; }</style>
```

`font-weight` は 200 / 300 / 350 / 400 / 500 / 700 / 900 に対応しています。
