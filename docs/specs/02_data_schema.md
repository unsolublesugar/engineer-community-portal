# 02. データスキーマ

## イベントデータ（`data/events/NNN.yaml`）

```yaml
# イベント基本情報
number: 76                           # イベント番号（必須）
title: "完全に理解したTalk #76"       # イベントタイトル（必須）
date: "2026-04-28"                   # 開催日（必須, YYYY-MM-DD）
event_url: "https://easy2.connpass.com/event/XXXXX/"  # イベントページURL（任意, connpass / Doorkeeper / Peatix / TECH PLAY / Meetup 等を自動判定）
youtube_url: "https://www.youtube.com/watch?v=XXXXX"     # YouTube配信URL（任意）
report_url: ""                       # イベントレポート記事URL（任意）
hashtag: "#完全に理解した"             # ハッシュタグ（任意）

# 発表一覧
talks:
  - title: "発表タイトル"              # 発表タイトル（必須）
    speaker:                          # 登壇者情報（必須）
      name: "表示名"                  # 表示名（必須）
      id: "speaker_id"               # speakers.yaml の id と一致させる（必須）
    slide_url: ""                     # スライドURL（任意）
    slide_embed_url: ""               # スライド埋め込みURL（任意, 自動生成対応）
    article_url: ""                   # 関連記事URL（任意）
    youtube_timestamp: ""             # YouTube内のタイムスタンプ（任意, 例: "0:15:30"）
    duration_minutes: 15              # 発表時間（分）（任意）
    tags: []                          # 発表のタグ（任意）
    description: ""                   # 発表概要（任意）
```

### 登壇者情報の記載ルール

イベントYAMLには `speaker.id` と `speaker.name` のみ記載する。
プロフィール情報（icon_url, twitter, github 等）は `data/speakers.yaml` で一元管理し、
ビルド時にマージされる。詳細は `.claude/rules/speaker_profile.md` を参照。

### 特別な speaker.id

- `tbd` — 発表者未定（開催予定イベント用）。登壇者一覧・企画ページから除外される
- `easy2` — コミュニティ全体の企画枠（チャレンジコーナー、ちょこっと深堀り等）。登壇者一覧から除外され、企画コーナーページに表示される

## フィールド詳細

### slide_embed_url について

ビルド時に `slide_url` から自動生成される。手動指定も可能。
各スライドサービスの埋め込みURL形式:

- **Speaker Deck**: `https://speakerdeck.com/player/XXXXX`
- **Google Slides**: `https://docs.google.com/presentation/d/XXXXX/embed`
- **SlideShare**: `https://www.slideshare.net/slideshow/embed_code/XXXXX`
- **Docswell**: `https://www.docswell.com/slide/XXXXX/embed`

### youtube_timestamp について

YouTube動画内の発表開始位置。`H:MM:SS` 形式。
ビルド時に `?t=` パラメータに変換される。

## コミュニティデータ（`data/community.yaml`）

```yaml
name: "EasyEasy"                          # サイト表示名
formal_name: "エンジニア達の「完全に理解した」Talk"  # 正式名称
description: "コミュニティの説明文"          # meta description 等に使用
community_url: "https://easy2.connpass.com/"  # コミュニティの所属ページ（connpass等のグループURL、ヘッダー「参加する」ボタンの遷移先）
youtube_channel: "https://www.youtube.com/@talk9929"
hashtag: "#完全に理解した"
schedule: "毎月最終火曜日 20:00〜"
zenn_url: ""                              # 任意
qiita_url: ""                             # 任意
discord_url: ""                           # 任意
slack_url: ""                             # 任意

stats:                                    # 統計情報
  since: 2019
  total_events: 76
  total_talks: 160

organizers:                               # 運営メンバー
  - name: "dach"
    role: "企画"
    twitter: "dach_chikin"
    icon_url: ""                          # アイコンURL（任意）
  - name: "unsoluble_sugar"
    role: "広報"
    twitter: "unsoluble_sugar"
    github: "unsolublesugar"              # GitHub（任意）
    zenn: "unsoluble_sugar"               # Zenn（任意）
    website: ""                           # Webサイト（任意）
    icon_url: ""
  - name: "mainyaa"
    role: "配信"
    twitter: "mainyaa"
    icon_url: ""
```
