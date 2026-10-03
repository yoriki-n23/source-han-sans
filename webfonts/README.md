# Kaku Sans JP Webフォント（Cloudflare Pages 配信）

`cidfont.ps.JP` から源ノ角ゴシック JP（Source Han Sans JP）の日本語サブセット OTF（7ウェイト）をビルドし、`unicode-range` で分割した WOFF2 と CSS を Cloudflare Pages へデプロイします。

## フォント名について

源ノ角ゴシックは SIL Open Font License 1.1 で、"Source" が予約フォント名（Reserved Font Name）です。サブセット化や分割をしたフォントは OFL の「改変版」にあたり、予約フォント名を使えません。そのため `split.py` は、配信用のフォントの名前を **Kaku Sans JP** に変えています（name テーブルと CFF の名前。日本語の名前「源ノ角ゴシック」も削除）。著作権表示とライセンスの記録はそのまま残し、`LICENSE.txt` も一緒に配信します。名前を変える場合は、`split.py` の `FAMILY` と `CSS_FILE` を書き換えてください。

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

## 使い方

```html
<link rel="stylesheet" href="https://source-han-sans.pages.dev/kaku-sans-jp.css">
<style>body { font-family: "Kaku Sans JP", sans-serif; }</style>
```

`font-weight` は 200 / 300 / 350 / 400 / 500 / 700 / 900 に対応しています。
