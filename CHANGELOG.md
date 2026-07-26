# Changelog

このプロジェクトの注目すべき変更を記録します。

形式は [Keep a Changelog](https://keepachangelog.com/ja/1.1.0/) に基づき、
バージョニングは [Semantic Versioning](https://semver.org/lang/ja/) に従います。

## [v1.2.0] - 2026-07-26

本家 [easy2-portal v1.2.0](https://github.com/unsolublesugar/easy2-portal/releases/tag/v1.2.0) のデザイン刷新をテンプレート側へ取り込みました。

### Changed
- サイト全体のデザインを刷新
  - プライマリカラー: `#3ea8ff` 系 → `#1668dc` 系
  - フォント: Inter → IBM Plex Sans JP
  - ボタン・バッジ・フィルター・検索ボックスをピル形状（`border-radius: 99px`）に統一
  - セクション見出しに青のアクセントバー（`.section-title`）と件数ピル（`.count-pill`）を追加
  - トップ: 年フィルターをセグメンテッドコントロール化、カード内の発表プレビューを淡青ボックスに
  - イベント詳細: レポート記事リンクをヘッダーカード内のピルに統合（単独バナーを廃止）、リソースリンクを色付きピル（動画=赤系 / 記事=緑系 / スライド=amber系）に、スライド埋め込みはピルの下へ移動
  - 登壇者一覧・詳細: 検索ボックスをピル型に、登壇履歴を淡青ボックス内のリストに
  - 企画コーナー: 縦積みリスト → カードグリッド
  - About: 各セクションを白カード化
  - 登壇者・運営メンバーの SNS リンクをアイコンからテキスト表記（X / GitHub / Qiita / Zenn / Web）に変更
- 日付表記をサイト全体で ISO 形式（`YYYY-MM-DD`）に統一（イベント詳細ヘッダーのみ `YYYY-MM-DD（曜）`）
  - Jinja2 フィルター `date_iso` / `date_iso_full` / `date_parts` を追加
- イベント詳細ページからハッシュタグのシェアピルを削除（`community.yaml` の `hashtag` を使うシェアボタンは変更なし）
- サンプルイベント `004.yaml` / `005.yaml` の開催日を未来日付に更新（開催予定表示・次回開催バナーの動作確認用）

### Added
- トップページに次回開催バナーを追加
  - 開催予定イベントのうち最も近い1件を、イベント一覧グリッドの外・上部に日付タイル付きの横長バナーで表示
  - 日付タイルの開始時刻は `community.yaml` の `schedule` から `HH:MM` を自動抽出
  - `event_url` があれば「参加登録する」、なければ「詳細を見る」に文言を切り替え
  - バナーに出したイベントは一覧グリッドから除外
- ヒーロー統計カードにアイコンタイルと単位表記（回 / 本）を追加

### Fixed
- モバイル表示の改善
  - ヒーローの「参加する」ボタンは次回開催バナーの「参加登録する」と導線が重複するため、開催予定イベントがない期間のみ表示
  - 小画面（440px 以下）でヘッダーナビが横溢れする不具合を修正
  - 極小画面（320px）ではロゴのサイト名を省略表示にし、ナビ4項目が収まるように修正
  - 登壇者一覧の登壇履歴の並び順を `#番号 → タイトル → 日付` に修正

### Docs
- PR 作成時の assignee / label 付与ルールを追記
- イベント YAML の `talks` に前座 / MC / 運営紹介を含めないルールを追記

## [v1.1.0] - 2026-04-29

### Added
- 開催予定イベントで確定LT登壇者を表示できるように ([#8](https://github.com/unsolublesugar/engineer-community-portal/pull/8))
  - `is_upcoming` をイベント日付ベースで判定（従来は `talks[0]` が TBD かで判定）
  - `tbd_count` をイベントに付与
  - 開催予定カード: 全TBD／部分確定／全確定 の3パターンでメッセージ切り替え
  - イベント詳細: 残TBD枠を1枚のカードに集約
- connpass 以外のイベントページへの差し替えに対応 ([#12](https://github.com/unsolublesugar/engineer-community-portal/pull/12))
  - URL のドメインから利用サービス（connpass / Doorkeeper / Peatix / TECH PLAY / Meetup）を自動判定
  - CTA・リンクラベル・申込ボタンの文言をサービス名で動的に切り替え
  - 未知ドメインは「イベントページ」にフォールバック
- 開催予定イベントのサンプルを2件追加 ([#11](https://github.com/unsolublesugar/engineer-community-portal/pull/11))
  - `data/events/004.yaml`: 未来日付 × 全TBD
  - `data/events/005.yaml`: 未来日付 × 部分確定

### Fixed
- `/live/` 形式 YouTube URL でタイムスタンプリンクが再生位置にジャンプしない不具合 ([#9](https://github.com/unsolublesugar/engineer-community-portal/pull/9))
  - ビルド時に `youtube_url` を `watch?v=VIDEO_ID` 形式に正規化

### Changed
- SlideShare の自動 iframe 埋め込みを廃止 ([#10](https://github.com/unsolublesugar/engineer-community-portal/pull/10))
  - SlideShare 側の anti-bot challenge により iframe 表示が機能しないため
  - スライドへの導線は「スライドを見る」外部リンクのみに

### Migration

YAML スキーマのフィールド名を変更しました。既存データを使っている場合は以下のリネームが必要です。

| ファイル | 旧 | 新 |
|---------|-----|-----|
| `data/events/NNN.yaml` | `connpass_url` | `event_url` |
| `data/community.yaml` | `connpass_url` | `community_url` |

ビルド側で URL から利用サービスを自動判定するため、connpass 固有の表示文言は除去されています。

## [v1.0.1] - 2026-04-14

- イベント詳細・登壇者詳細ページに X シェア導線を追加 ([#3](https://github.com/unsolublesugar/engineer-community-portal/pull/3))
- Git ワークフローにブランチ運用ルールを追加 ([#2](https://github.com/unsolublesugar/engineer-community-portal/pull/2))
- イベント詳細ページの前後ナビゲーションを左右入れ替え ([#1](https://github.com/unsolublesugar/engineer-community-portal/pull/1))

## [v1.0.0] - 2026-04-13

- 初回リリース

[v1.2.0]: https://github.com/unsolublesugar/engineer-community-portal/compare/v1.1.0...v1.2.0
[v1.1.0]: https://github.com/unsolublesugar/engineer-community-portal/compare/v1.0.1...v1.1.0
[v1.0.1]: https://github.com/unsolublesugar/engineer-community-portal/compare/v1.0.0...v1.0.1
[v1.0.0]: https://github.com/unsolublesugar/engineer-community-portal/releases/tag/v1.0.0
