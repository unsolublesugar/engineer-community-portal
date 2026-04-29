# Changelog

このプロジェクトの注目すべき変更を記録します。

形式は [Keep a Changelog](https://keepachangelog.com/ja/1.1.0/) に基づき、
バージョニングは [Semantic Versioning](https://semver.org/lang/ja/) に従います。

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

[v1.1.0]: https://github.com/unsolublesugar/engineer-community-portal/compare/v1.0.1...v1.1.0
[v1.0.1]: https://github.com/unsolublesugar/engineer-community-portal/compare/v1.0.0...v1.0.1
[v1.0.0]: https://github.com/unsolublesugar/engineer-community-portal/releases/tag/v1.0.0
