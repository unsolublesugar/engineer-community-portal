# 登壇者プロフィール管理ルール

## データ管理方針

登壇者のプロフィール情報は **`data/speakers.yaml`** で一元管理する。
各イベントYAML（`data/events/NNN.yaml`）には `speaker.id` と `speaker.name` のみ記載し、
SNSアカウントやアイコンURL等のプロフィール情報は記載しない。

ビルド時に `speakers.yaml` の情報がイベントYAMLの `speaker.id` とマージされる。

## アイコン画像の取得・適用優先度

登壇者のアイコン画像URLは以下の優先度で適用する。ビルド時に自動解決される。

1. **icon_url**: `icon_url` フィールドに直接指定された URL（X(pbs.twimg.com)、connpass(media.connpass.com) 等）
2. **GitHub**: `https://github.com/{github_username}.png`（icon_url 未設定時のフォールバック）

※ unavatar.io/x はレート制限が厳しく不安定なため使用しない。
※ Xのアイコンを優先したい場合は、icon_url に pbs.twimg.com の URL を設定する。

## speakers.yaml のフォーマット

```yaml
- id: speaker_id             # 一意のID（必須）
  name: 表示名               # 表示名（必須）
  icon_url: ""               # connpassアイコン等（任意、上記優先度で自動解決）
  twitter: ""                # X(Twitter)アカウント名（@なし）
  github: ""                 # GitHubアカウント名
  qiita: ""                  # Qiitaアカウント名（任意）
  zenn: ""                   # Zennアカウント名（任意）
  website: ""                # Webサイト（任意）
```

## イベントYAML での登壇者の記述

```yaml
talks:
  - title: 発表タイトル
    speaker:
      name: 表示名           # 可読性のために残す
      id: speaker_id         # speakers.yaml の id と一致させる（必須）
    slide_url: ...
```

※ プロフィール情報（icon_url, twitter, github 等）はイベントYAMLに記載しない。

## プロフィール情報の収集手順

新しい登壇者の情報を追加する際は、以下の順序で調査する：

1. connpass のイベントページ → 参加者一覧から connpass ユーザー名を特定
2. connpass のユーザープロフィール（`https://connpass.com/user/{username}/`）→ X, GitHub リンクを取得
3. YouTube アーカイブ動画の概要欄 → 登壇者名・SNS アカウントの確認
4. 特定できない場合は `id` に仮の値を設定し、手動確認が必要な旨をコメントで残す

## 注意事項

- `icon_url` は X や connpass 等から取得した直接URLを格納する（最優先で使用される）
- ビルド時に `icon_url` → `github` の優先度で最終的なアイコンURLが決まる
- X / GitHub のアイコンは外部サービス経由のため、ローカルファイル閲覧時は表示されない場合がある
- プロフィール情報の変更は `data/speakers.yaml` のみを編集すれば全イベントページに反映される
