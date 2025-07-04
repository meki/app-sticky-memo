# App Sticky Memo

> 📖 **English** | [English Documentation](../Readme.md)

アプリ毎にメモを残せる Windows 専用アプリです。
ユーザーが使用するアプリを切り替えると、自動的にそのアプリに関連するメモが表示されます。
メモはアプリごとに保存され、アプリを切り替えることで異なるメモを簡単に確認できます。
そのため、たまにしか使わないアプリのメモも、アプリを切り替えるだけで簡単に確認できます。

## 機能

- **アプリごとにメモを保存**: 各アプリケーション（exe 名）ごとに独立したメモファイルを自動作成
- **自動切り替え**: アプリを切り替えると自動的に関連するメモに切り替わり
- **設定機能**: データ保存ディレクトリをカスタマイズ可能
- **ウィンドウ位置の記憶**: アプリ終了時にウィンドウの位置とサイズを保存し、次回起動時に復元
- **常に最前面表示**: チェックボックスでアプリを常に最前面に表示可能
- **マークダウン対応**: メモファイルは Markdown 形式で保存され、見出しやリスト、リンクなどが使用可能
- **自動保存**: メモの内容は自動的に保存されるため、手動での保存は不要
- **多言語対応**: UI テキストが外部ファイル化されており、将来的な言語追加が容易

## インストール方法

1. Release ページ から最新のリリースをダウンロードします。
2. ダウンロードした ZIP ファイルを解凍します。
3. 解凍したフォルダ内の `AppStickyMemo.exe` を実行します。

## 使用方法

1. **アプリ起動**: アプリを起動すると、現在アクティブなアプリが検出され、対応するメモファイルが自動作成されます
2. **設定**: 右上の歯車ボタンから設定パネルを開き、メモファイルの保存先ディレクトリを変更できます
3. **アプリ切り替え**: 別のアプリケーションに切り替えると、そのアプリに関連するメモファイルが自動作成されます
4. **ウィンドウサイズ**: ウィンドウのサイズや位置を変更すると、アプリ終了時に自動保存され、次回起動時に復元されます

## メモファイルについて

- メモファイルは `[メモ名].md` の形式で保存されます
- ファイルは Markdown 形式なので、テキストエディタで直接編集することも可能です
- デフォルトの保存先: `C:\Users\[ユーザー名]\Documents\StickyMemos\`

### アプリとメモの対応関係

- データ保存ディレクトリに `mapping.yaml` ファイルが自動作成されます
- このファイルで実行ファイル名（exe 名）とメモ名の対応関係を管理します
- デフォルトでは exe 名 = メモ名 として自動的にマッピングが作成されます
- 将来的には UI でこのマッピングを編集できる機能を追加予定です

**マッピングファイル例（mapping.yaml）:**

```yaml
version: "1.0"
description: "Mapping between exe names and memo names"
mappings:
  - exe_name: "chrome.exe"
    memo_name: "Chrome"
  - exe_name: "chrome_64.exe"
    memo_name: "Chrome" # 同じメモを共有
  - exe_name: "メモ帳.exe"
    memo_name: "メモ帳"
  - exe_name: "Visual Studio Code.exe"
    memo_name: "VSCode"
  - exe_name: "测试程序.exe"
    memo_name: "テストプログラム"
```

これにより、日本語や中国語などの多言語 exe 名にも対応し、同一プログラムの異なるバージョン（32bit/64bit 版など）で同じメモを共有できます。

## 開発

### 必要な環境

- Python 3.11+
- uv パッケージマネージャー

### セットアップ

```bash
# リポジトリをクローン
git clone <repository-url>
cd app-sticky-memo

# 依存関係をインストール
uv sync

# アプリケーションを実行
uv run python app.py
```

### コード品質

プロジェクトではコード品質のために pre-commit フックを使用しています：

```bash
# 全ての品質チェックを実行
uv run pre-commit run --all-files
```

### プロジェクト構造

```
app-sticky-memo/
├── app.py                 # メインアプリケーションエントリーポイント
├── src/
│   ├── components/        # UIコンポーネント
│   │   ├── header.py      # タイトルとコントロールのヘッダー
│   │   ├── memo_editor.py # 自動保存付きメモエディター
│   │   └── settings_panel.py # 設定パネル
│   ├── core/              # コアビジネスロジック
│   │   ├── foreground_monitor.py # フォアグラウンドアプリ追跡
│   │   ├── memo_manager.py # アプリ別メモファイル管理
│   │   └── settings_manager.py # アプリ設定管理
│   └── locales/           # 国際化
│       ├── i18n.py        # I18nマネージャー
│       ├── ja.yaml        # 日本語翻訳
│       └── en.yaml        # 英語翻訳
├── docs/
│   └── Readme.ja.md       # 日本語ドキュメント
└── pyproject.toml         # プロジェクト設定
```

## アーキテクチャ

アプリケーションはモジュラーアーキテクチャに従っています：

- **UI コンポーネント**: 明確な責任を持つ各 UI 要素の個別クラス
- **コアロジック**: UI 関心事から分離されたビジネスロジック
- **設定管理**: JSON ストレージによる永続化設定
- **メモ管理**: アプリごとのファイル処理と自動保存
- **フォアグラウンド監視**: アクティブアプリを追跡するバックグラウンドサービス
- **国際化**: YAML ベースの翻訳システム

## 貢献

1. リポジトリをフォーク
2. フィーチャーブランチを作成
3. 変更を行う
4. コード品質チェックを実行: `uv run pre-commit run --all-files`
5. プルリクエストを提出

## ライセンス

このプロジェクトは MIT ライセンスの下でライセンスされています - 詳細は [LICENSE](../LICENSE) ファイルを参照してください。
