# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

twitchTransFreeNextは、Twitchチャットのメッセージを自動的に翻訳するボットです。Twitch IRCに接続し、リアルタイムで複数言語間の翻訳を実行します。

## アーキテクチャ

### コアモジュール

- **twitchTransFN.py**: メインエントリーポイント。TwitchIOベースのボットクラスを実装し、メッセージ処理と翻訳のオーケストレーションを担当
- **database_controller.py**: SQLiteを使用した翻訳キャッシュ。既訳語を保存し、API呼び出しを削減（特にDeepLの文字数制限対策）
- **tts.py**: テキスト読み上げ機能。gTTSまたはCeVIOをサポートし、専用スレッドでキュー処理
- **sound.py**: サウンドファイル再生機能（`!sound`コマンド用）。専用スレッドでキュー処理
- **config.py**: 全ての設定を管理（チャンネル名、OAuth、翻訳エンジン、TTS設定など）

### データフロー

1. TwitchIOがメッセージを受信 → `event_message()`
2. エモート、無視ユーザ、無視テキストのフィルタリング
3. 言語検出（google_trans_newまたはGAS経由）
4. データベースキャッシュをチェック
5. キャッシュミスの場合、翻訳実行（DeepL優先、フォールバックでGoogle）
6. 翻訳結果をデータベースに保存
7. Twitchチャットに投稿
8. TTSキューに入力・出力テキストを追加（設定に応じて）

### スレッドアーキテクチャ

- **メインスレッド**: TwitchIO asyncioイベントループ
- **TTSスレッド**: `tts.voice_synth()` - テキスト読み上げをキューから処理
- **サウンドスレッド**: `sound.sound_play()` - サウンドファイル再生をキューから処理

## 開発コマンド

### ローカル実行

```bash
# 依存関係のインストール
pip install -r requirements.txt

# config.pyを設定してから実行
python twitchTransFN.py
```

### ビルド

```bash
# 各OS向けバイナリのビルド（PyInstaller使用）
python build.py windows      # Windows版
python build.py linux        # Linux版
python build.py macos_M1     # macOS Apple Silicon版
python build.py macos_Intel  # macOS Intel版
```

ビルドプロセス:
- `cacert.pem`を自動ダウンロード（SSL証明書検証用）
- PyInstallerで単一実行ファイルを生成
- バージョン番号はtwitchTransFN.pyから自動抽出
- 出力ファイルは`dist/`フォルダに生成

### テスト

このプロジェクトには自動テストがありません。動作確認はTwitchチャットでの実行によって行います。

## 重要な設定ファイル

### config.py

必須設定:
- `Twitch_Channel`: 翻訳対象のチャンネル名
- `Trans_Username`: ボット用のTwitchユーザ名
- `Trans_OAUTH`: https://twitchapps.com/tmi/ で取得

翻訳エンジン設定:
- `Translator`: `'deepl'`または`'google'`
- `GAS_URL`: Google Apps Script経由で翻訳する場合のURL
- `GoogleTranslate_suffix`: 使用するGoogle翻訳ドメイン（例: 'co.jp'）

## 特殊機能

### データベースキャッシュ

`database_controller.py`は翻訳済みテキストをSQLiteに保存し、同一テキストの再翻訳を防ぎます。これによりDeepLの無料プランの文字数制限に達するのを防ぎます。データベースファイルが50MBを超えると自動削除されます。

### _MEIフォルダクリーンアップ

PyInstallerでビルドされた実行ファイルは一時フォルダ（`_MEI*`）を作成します。`CLEANMEIFOLDERS()`関数が起動時に古い_MEIフォルダを削除します（twitchTransFN.py:203-236）。

### macOS互換性

macOS環境では`AppKit`がない場合、`afplay`コマンドラインツールをフォールバックとして使用します（tts.py:26-43, sound.py:22-41）。

### エモート処理

Twitchエモート、サードパーティエモート（BTTV/FFZ/7TV）、Unicode絵文字を検出・除去してから翻訳します（twitchTransFN.py:298-352）。

## 注意事項

- config.pyはリポジトリに含まれていますが、実際の認証情報を含むべきではありません
- PyInstallerビルド時、cacert.pemを同梱してSSLエラーを回避（twitchTransFN.py:136-152）
- CeVIO TTSはWindows専用機能です（Win32COMを使用）
- デバッグモードは`config.py`の`Debug = True`で有効化
