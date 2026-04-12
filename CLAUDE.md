# Engineer Community Portal

エンジニアコミュニティのLTイベント情報ポータルサイト（静的サイト）

## 応答ルール

- 日本語で応答すること
- データ/テンプレート変更後は `python src/build.py` でリビルドすること

## 開発コマンド

```bash
pip install -r requirements.txt   # 依存パッケージ
python src/build.py               # サイトビルド → output/ に出力
```

## 構成概要

- **ビルド**: Python + Jinja2 → 静的HTML生成 → GitHub Pages
- **データ**: `data/events/NNN.yaml`（イベント）、`data/speakers.yaml`（登壇者マスター）、`data/community.yaml`（サイト設定）
- **テンプレート**: `src/templates/`（base, index, event_detail, speakers, challenge, about, 404）
- **アセット**: `assets/`（css, js, images）
- **設定**: `src/config/settings.py`
- **出力**: `output/`（git管理外、クリーンURL形式 `ページ名/index.html`）

## データ追加ワークフロー

1. `data/events/` に YAML 追加（例: `004.yaml`）
2. 新規登壇者は `data/speakers.yaml` に追加
3. `python src/build.py` でビルド
4. Git push → GitHub Actions で自動デプロイ

詳細: 登壇者管理は `.claude/rules/speaker_profile.md`、データスキーマは `docs/specs/02_data_schema.md` を参照。
