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

## Cloudflare Pages へのデプロイ

### 通常：Git 連携（APIトークン不要）

Cloudflare ダッシュボード › Workers & Pages › 作成 › Pages › Git に接続 で、このリポジトリを選び、次のように設定します。

| 項目 | 値 |
|---|---|
| プロジェクト名 | `source-han-sans` |
| 本番ブランチ | `master` |
| フレームワーク プリセット | None |
| ビルドコマンド | `pip install -r webfonts/requirements.txt && webfonts/build.sh` |
| ビルド出力ディレクトリ | `dist/site` |
| 環境変数 | `PYTHON_VERSION` = `3.12` |

以後、`master` に push するたびに自動でデプロイされ、`https://source-han-sans.pages.dev/` で公開されます。

### 予備：GitHub Actions（手動実行）

Git 連携が使えない場合は、`CLOUDFLARE_API_TOKEN`（権限は Account › Cloudflare Pages › Edit のみ）と `CLOUDFLARE_ACCOUNT_ID` を GitHub の Settings › Secrets and variables › Actions に登録し、Actions タブから「Deploy web fonts to Cloudflare Pages」を手動実行します。

## 使い方

```html
<link rel="stylesheet" href="https://source-han-sans.pages.dev/source-han-sans-jp.css">
<style>body { font-family: "Source Han Sans JP", sans-serif; }</style>
```

`font-weight` は 200 / 300 / 350 / 400 / 500 / 700 / 900 に対応しています。
