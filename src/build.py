#!/usr/bin/env python3
"""Engineer Community Portal - 静的サイトビルドスクリプト"""

import json
import re
import shutil
import sys
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader

from config.settings import (
    ASSETS_DIR,
    DATA_DIR,
    EVENTS_DIR,
    OUTPUT_DIR,
    SITE_DESCRIPTION,
    SITE_NAME,
    SITE_OG_IMAGE,
    SITE_TITLE,
    SITE_URL,
    TEMPLATES_DIR,
)


def load_yaml(filepath: Path) -> dict:
    """YAMLファイルを読み込む"""
    with open(filepath, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_all_events() -> list[dict]:
    """全イベントデータを読み込み、番号降順でソートして返す"""
    events = []
    for yaml_file in sorted(EVENTS_DIR.glob("*.yaml"), reverse=True):
        event = load_yaml(yaml_file)
        if event:
            if event.get("youtube_url"):
                event["youtube_url"] = normalize_youtube_url(event["youtube_url"])
            # 発表数をカウント（TBD除外）
            talks = event.get("talks", [])
            event["talk_count"] = len([
                t for t in talks
                if t.get("speaker", {}).get("id") != "tbd"
            ])
            events.append(event)
    return events


def load_speakers_master() -> dict[str, dict]:
    """登壇者マスターデータを読み込む

    Returns:
        speaker_id をキー、プロフィール情報を値とする辞書
    """
    speakers_file = DATA_DIR / "speakers.yaml"
    if not speakers_file.exists():
        print("  ⚠ data/speakers.yaml が見つかりません")
        return {}

    speakers_list = load_yaml(speakers_file) or []
    return {s["id"]: s for s in speakers_list if s.get("id")}


def merge_speaker_profile(speaker: dict, master: dict[str, dict]) -> dict:
    """イベントYAMLのspeaker情報にマスターデータをマージする

    マスター側のプロフィール情報（name, icon_url, twitter, github, qiita, zenn, website）を
    ベースとし、イベントYAML側にも値がある場合はイベント側を優先する（個別上書き用途）。

    Args:
        speaker: イベントYAMLのspeaker辞書
        master: 登壇者マスター辞書（id→プロフィール）
    Returns:
        マージ済みspeaker辞書
    """
    sid = speaker.get("id", "")
    if not sid or sid not in master:
        return speaker

    profile = master[sid]
    merged = dict(speaker)  # イベント側をコピー

    # マスターの情報をベースに、イベント側に値がなければ補完
    for key in ("name", "icon_url", "twitter", "github", "qiita", "zenn", "website"):
        master_val = profile.get(key, "")
        event_val = merged.get(key, "")
        if master_val and not event_val:
            merged[key] = master_val

    return merged


def load_community() -> dict:
    """コミュニティデータを読み込む"""
    community_file = DATA_DIR / "community.yaml"
    if community_file.exists():
        return load_yaml(community_file)
    return {}


def resolve_speaker_icon(speaker: dict) -> str:
    """登壇者のアイコンURLを優先度に従って解決する

    優先度: icon_url（X等の手動指定） > GitHub > デフォルト
    ※ unavatar.io/x はレート制限が厳しいため使用しない

    Args:
        speaker: 登壇者情報の辞書
    Returns:
        アイコン画像URL（解決できない場合は空文字列）
    """
    icon_url = speaker.get("icon_url", "")
    github = speaker.get("github", "")

    if icon_url:
        return icon_url
    if github:
        return f"https://github.com/{github}.png"
    return ""


def build_speakers(events: list[dict], master: dict[str, dict]) -> list[dict]:
    """全イベントから登壇者情報を集約する

    Args:
        events: 全イベントデータ
        master: 登壇者マスター辞書（speakers.yaml由来）
    """
    speakers_map: dict[str, dict] = {}

    for event in events:
        for talk in event.get("talks", []):
            speaker = talk.get("speaker", {})
            sid = speaker.get("id", "")
            if not sid or sid in ("tbd", "easy2"):
                continue

            if sid not in speakers_map:
                # マスターからプロフィール情報を取得
                profile = master.get(sid, {})
                speakers_map[sid] = {
                    "id": sid,
                    "name": profile.get("name") or speaker.get("name", sid),
                    "icon_url": profile.get("icon_url", ""),
                    "github": profile.get("github", ""),
                    "twitter": profile.get("twitter", ""),
                    "qiita": profile.get("qiita", ""),
                    "zenn": profile.get("zenn", ""),
                    "website": profile.get("website", ""),
                    "talks": [],
                }

            speakers_map[sid]["talks"].append({
                "title": talk.get("title", ""),
                "event_number": event.get("number"),
                "event_title": event.get("title", ""),
                "date": event.get("date", ""),
                "tags": talk.get("tags", []),
                "slide_url": talk.get("slide_url", ""),
                "article_url": talk.get("article_url", ""),
                "youtube_timestamp": talk.get("youtube_timestamp", ""),
                "youtube_url": event.get("youtube_url", ""),
                "description": talk.get("description", ""),
            })

    # アイコンURLを優先度に従って解決
    for s in speakers_map.values():
        s["resolved_icon_url"] = resolve_speaker_icon(s)

    # 登壇回数でソート（降順）
    speakers = sorted(
        speakers_map.values(),
        key=lambda s: len(s["talks"]),
        reverse=True,
    )
    for s in speakers:
        s["talk_count"] = len(s["talks"])
        # 発表を開催日降順（新しい順）でソート
        s["talks"].sort(key=lambda t: t.get("date", ""), reverse=True)
        # 最新の登壇日を記録（ソート用）
        dates = [t["date"] for t in s["talks"] if t.get("date")]
        s["latest_date"] = max(dates) if dates else ""

    return speakers


def timestamp_to_seconds(timestamp: str) -> int:
    """'H:MM:SS' or 'MM:SS' 形式のタイムスタンプを秒数に変換"""
    parts = timestamp.split(":")
    if len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    elif len(parts) == 2:
        return int(parts[0]) * 60 + int(parts[1])
    return 0


def extract_youtube_video_id(url: str) -> str:
    """YouTube URLからビデオIDを抽出する

    対応するURL形式:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/live/VIDEO_ID
    """
    if not url:
        return ""
    if "watch?v=" in url:
        return url.split("watch?v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    elif "/live/" in url:
        return url.split("/live/")[1].split("?")[0]
    return ""


def normalize_youtube_url(url: str) -> str:
    """YouTube URLを `watch?v=VIDEO_ID` 形式に正規化する。

    テンプレートで `&t=Xs` を付与する都合上、URLは `?v=` を含む形式である必要がある。
    `/live/` や `youtu.be/` 形式のままだと `&t=` が `?` の前に付き再生位置が無視されるため、
    ここで `watch?v=` 形式に揃える。
    """
    if not url:
        return ""
    video_id = extract_youtube_video_id(url)
    if not video_id:
        return url
    return f"https://www.youtube.com/watch?v={video_id}"


def youtube_embed_url(url: str, timestamp: str = "") -> str:
    """YouTube URLを埋め込みURLに変換"""
    video_id = extract_youtube_video_id(url)
    if not video_id:
        return ""

    embed = f"https://www.youtube-nocookie.com/embed/{video_id}"
    if timestamp:
        seconds = timestamp_to_seconds(timestamp)
        embed += f"?start={seconds}"
    return embed


## ──────────────────────────────────────────────
## スライド埋め込みURL 自動生成
## ──────────────────────────────────────────────

SPEAKERDECK_CACHE_FILE = DATA_DIR / "speakerdeck_cache.json"


def _load_speakerdeck_cache() -> dict[str, str]:
    """Speaker Deck oEmbedキャッシュを読み込む"""
    if SPEAKERDECK_CACHE_FILE.exists():
        with open(SPEAKERDECK_CACHE_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_speakerdeck_cache(cache: dict[str, str]) -> None:
    """Speaker Deck oEmbedキャッシュを保存する"""
    with open(SPEAKERDECK_CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)


def _fetch_speakerdeck_embed(slide_url: str, cache: dict[str, str]) -> str:
    """Speaker Deck oEmbed APIで埋め込みURLを取得する

    結果はcacheに保存され、次回以降はAPIを呼ばない。
    """
    if slide_url in cache:
        return cache[slide_url]

    oembed_api = f"https://speakerdeck.com/oembed.json?url={slide_url}"
    try:
        req = urllib.request.Request(oembed_api, headers={"User-Agent": "EasyEasyBuilder/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            html = data.get("html", "")
            m = re.search(r'src="([^"]+)"', html)
            if m:
                embed_url = m.group(1)
                # https → プロトコル付きに正規化
                if embed_url.startswith("//"):
                    embed_url = "https:" + embed_url
                cache[slide_url] = embed_url
                return embed_url
    except (urllib.error.URLError, json.JSONDecodeError, OSError, ValueError) as e:
        print(f"    ⚠ Speaker Deck oEmbed failed: {e}")

    cache[slide_url] = ""
    return ""


def generate_slide_embed_url(slide_url: str, sd_cache: dict[str, str]) -> str:
    """slide_url から各スライドサービスの埋め込みURLを自動生成する

    対応サービス:
    - Speaker Deck (oEmbed API経由)
    - Docswell
    - Google Slides
    - slides.com

    Args:
        slide_url: スライドの閲覧URL
        sd_cache: Speaker Deck oEmbedキャッシュ dict
    Returns:
        埋め込み用iframe src URL（非対応の場合は空文字列）
    """
    if not slide_url:
        return ""

    # --- Google Slides ---
    if "docs.google.com/presentation" in slide_url:
        m = re.search(r"/d/([a-zA-Z0-9_-]+)", slide_url)
        if m:
            return f"https://docs.google.com/presentation/d/{m.group(1)}/embed"

    # --- Docswell ---
    if "docswell.com/s/" in slide_url:
        # URL例: https://www.docswell.com/s/USERNAME/KYVY7E-2026-02-20-182013[/PAGE][#pN]
        # 埋め込みURLにはハイフン前のslug部分のみ使用する
        # 例: KYVY7E-2026-02-20-182013 → KYVY7E
        after_s = slide_url.split("/s/")[1]  # "USERNAME/SLUG-DATE/1#p1" etc.
        parts = after_s.split("/")
        if len(parts) >= 2:
            slug_full = parts[1].split("#")[0]  # ページ番号・アンカー除去
            slug = slug_full.split("-")[0]  # 日付サフィックス除去
            return f"https://www.docswell.com/slide/{slug}/embed"

    # --- SlideShare ---
    # SlideShare は anti-bot challenge により iframe 埋め込みが不安定なため、
    # 自動 embed は生成せず、外部リンクのみとする。

    # --- slides.com ---
    if "slides.com/" in slide_url and "/embed" not in slide_url:
        # URL例: https://slides.com/USERNAME/DECK → /embed を付与
        clean = slide_url.split("?")[0].split("#")[0].rstrip("/")
        return clean + "/embed"

    # --- Speaker Deck ---
    if "speakerdeck.com/" in slide_url and "/player/" not in slide_url:
        return _fetch_speakerdeck_embed(slide_url, sd_cache)

    return ""


def get_years(events: list[dict]) -> list[int]:
    """イベントから年度一覧を取得"""
    years = set()
    for event in events:
        date_str = event.get("date", "")
        if date_str:
            try:
                years.add(int(date_str[:4]))
            except (ValueError, IndexError):
                pass
    return sorted(years, reverse=True)


def setup_jinja_env() -> Environment:
    """Jinja2環境をセットアップ"""
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=True,
    )

    # カスタムフィルター
    env.filters["youtube_embed"] = youtube_embed_url
    env.filters["timestamp_seconds"] = timestamp_to_seconds

    # グローバル変数
    env.globals["site_name"] = SITE_NAME
    env.globals["site_title"] = SITE_TITLE
    env.globals["site_description"] = SITE_DESCRIPTION
    env.globals["site_url"] = SITE_URL
    env.globals["site_og_image"] = SITE_OG_IMAGE
    # base_path はページごとにコンテキストで渡す（相対パス対応）
    env.globals["build_time"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    env.globals["current_year"] = datetime.now().year

    return env


def build_site():
    """サイト全体をビルド"""
    print("🔨 Engineer Community Portal - ビルド開始")

    # 出力ディレクトリをクリーンアップ
    if OUTPUT_DIR.exists():
        for item in OUTPUT_DIR.iterdir():
            if item.is_dir():
                shutil.rmtree(item, ignore_errors=True)
            else:
                try:
                    item.unlink()
                except OSError:
                    pass
    else:
        OUTPUT_DIR.mkdir(parents=True)

    # データ読み込み
    events = load_all_events()
    community = load_community()
    speakers_master = load_speakers_master()
    speakers = build_speakers(events, speakers_master)
    years = get_years(events)

    print(f"  イベント数: {len(events)}")
    print(f"  登壇者数: {len(speakers)}")

    # Jinja2セットアップ
    env = setup_jinja_env()

    # 共通コンテキスト
    common_ctx = {
        "community": community,
        "years": years,
        "base_path": ".",  # トップレベルページ用
    }

    # 1. トップページ
    print("  📄 index.html")
    tpl = env.get_template("index.html")
    html = tpl.render(events=events, **common_ctx)
    (OUTPUT_DIR / "index.html").write_text(html, encoding="utf-8")

    # 2. イベント詳細ページ
    events_dir = OUTPUT_DIR / "events"
    events_dir.mkdir(exist_ok=True)
    tpl = env.get_template("event_detail.html")

    # Speaker Deck oEmbedキャッシュの読み込み
    sd_cache = _load_speakerdeck_cache()
    sd_cache_dirty = False

    # イベント番号のセットを作成（前後ナビゲーション用）
    event_numbers = sorted(e.get("number", 0) for e in events)

    for event in events:
        num = event.get("number", 0)
        event_dir = events_dir / f"{num:03d}"
        event_dir.mkdir(exist_ok=True)
        print(f"  📄 events/{num:03d}/index.html")

        # 前後イベント番号を算出
        idx = event_numbers.index(num)
        prev_event_num = event_numbers[idx - 1] if idx > 0 else None
        next_event_num = event_numbers[idx + 1] if idx < len(event_numbers) - 1 else None

        # YouTubeビデオID・埋め込みURLを生成
        event["youtube_video_id"] = extract_youtube_video_id(
            event.get("youtube_url", "")
        )
        event["youtube_embed"] = youtube_embed_url(
            event.get("youtube_url", "")
        )
        for talk in event.get("talks", []):
            if event.get("youtube_url") and talk.get("youtube_timestamp"):
                talk["youtube_embed"] = youtube_embed_url(
                    event["youtube_url"], talk["youtube_timestamp"]
                )
            else:
                talk["youtube_embed"] = ""

            # 登壇者情報をマスターとマージし、アイコンURLを解決
            speaker = merge_speaker_profile(talk.get("speaker", {}), speakers_master)
            talk["speaker"] = speaker
            speaker["resolved_icon_url"] = resolve_speaker_icon(speaker)

            # スライド埋め込みURLを自動生成（YAMLに明示指定がなければ）
            if not talk.get("slide_embed_url") and talk.get("slide_url"):
                old_cache_size = len(sd_cache)
                talk["slide_embed_url"] = generate_slide_embed_url(
                    talk["slide_url"], sd_cache
                )
                if len(sd_cache) != old_cache_size:
                    sd_cache_dirty = True

        # イベント詳細ページは2階層深いので base_path を調整
        html = tpl.render(
            event=event,
            prev_event_num=prev_event_num,
            next_event_num=next_event_num,
            base_path="../..",
            **{k: v for k, v in common_ctx.items() if k != "base_path"},
        )
        (event_dir / "index.html").write_text(html, encoding="utf-8")

    # Speaker Deck キャッシュを保存
    if sd_cache_dirty:
        _save_speakerdeck_cache(sd_cache)
        print(f"  💾 Speaker Deck キャッシュ保存 ({len(sd_cache)} 件)")

    # 3. コミュニティ概要ページ
    print("  📄 about/index.html")
    about_dir = OUTPUT_DIR / "about"
    about_dir.mkdir(exist_ok=True)
    tpl = env.get_template("about.html")
    html = tpl.render(
        total_events=len(events),
        total_speakers=len(speakers),
        total_talks=sum(e.get("talk_count", 0) for e in events),
        base_path="..",
        **{k: v for k, v in common_ctx.items() if k != "base_path"},
    )
    (about_dir / "index.html").write_text(html, encoding="utf-8")

    # 4. チャレンジコーナーページ
    print("  📄 challenge/index.html")
    challenge_talks = []
    deep_dive_talks = []
    for event in events:
        for talk in event.get("talks", []):
            if talk.get("speaker", {}).get("id") == "easy2":
                item = {
                    "title": talk.get("title", ""),
                    "event_number": event.get("number"),
                    "date": event.get("date", ""),
                    "youtube_url": event.get("youtube_url", ""),
                    "youtube_timestamp": talk.get("youtube_timestamp", ""),
                }
                if "チャレンジコーナー" in talk.get("title", ""):
                    challenge_talks.append(item)
                else:
                    deep_dive_talks.append(item)
    challenge_dir = OUTPUT_DIR / "challenge"
    challenge_dir.mkdir(exist_ok=True)
    tpl = env.get_template("challenge.html")
    html = tpl.render(
        challenges=challenge_talks,
        deep_dives=deep_dive_talks,
        base_path="..",
        **{k: v for k, v in common_ctx.items() if k != "base_path"},
    )
    (challenge_dir / "index.html").write_text(html, encoding="utf-8")

    # 5. 登壇者一覧ページ
    print("  📄 speakers/index.html")
    speakers_dir = OUTPUT_DIR / "speakers"
    speakers_dir.mkdir(exist_ok=True)
    tpl = env.get_template("speakers.html")
    html = tpl.render(
        speakers=speakers,
        base_path="..",
        **{k: v for k, v in common_ctx.items() if k != "base_path"},
    )
    (speakers_dir / "index.html").write_text(html, encoding="utf-8")

    # 5-2. 登壇者個別ページ
    tpl = env.get_template("speaker_detail.html")
    for speaker in speakers:
        speaker_dir = speakers_dir / speaker["id"]
        speaker_dir.mkdir(exist_ok=True)
        print(f"  📄 speakers/{speaker['id']}/index.html")
        html = tpl.render(
            speaker=speaker,
            base_path="../..",
            **{k: v for k, v in common_ctx.items() if k != "base_path"},
        )
        (speaker_dir / "index.html").write_text(html, encoding="utf-8")

    # 6. 404ページ
    print("  📄 404.html")
    tpl = env.get_template("404.html")
    html = tpl.render(**common_ctx)
    (OUTPUT_DIR / "404.html").write_text(html, encoding="utf-8")

    # アセットをコピー
    print("  📁 アセットをコピー中...")
    for subdir in ["css", "js", "images"]:
        src = ASSETS_DIR / subdir
        dst = OUTPUT_DIR / subdir
        if src.exists():
            shutil.copytree(src, dst, dirs_exist_ok=True)

    print("✅ ビルド完了！")
    print(f"  出力先: {OUTPUT_DIR}")


if __name__ == "__main__":
    build_site()
