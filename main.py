import json
import os
import sys
from pathlib import Path

from scrapers import kodaira, koganei, kokubunji, fuchu, tachikawa, hino, akishima, hachioji
import notify

DATA_FILE = Path(__file__).parent / "data" / "previous.json"

CITIES = {
    "小平市": kodaira,
    "小金井市": koganei,
    "国分寺市": kokubunji,
    "府中市": fuchu,
    "立川市": tachikawa,
    "日野市": hino,
    "昭島市": akishima,
    "八王子市": hachioji,
}


def load_previous() -> dict:
    """前回データを読み込む。ファイルがなければ空の辞書を返す。"""
    if DATA_FILE.exists():
        try:
            with DATA_FILE.open("r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            print(f"[main] previous.json の読み込みに失敗しました: {e}")
    return {}


def save_current(data: dict) -> None:
    """現在のデータを previous.json に書き込む。"""
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("[main] データを previous.json に保存しました。")


def detect_increases(previous: dict, current: dict) -> dict:
    """
    previous と current を比較し、空き数が増加した施設を返す。
    返値: {"市名": [{"facility": str, "prev": int, "curr": int}]}
    """
    increases = {}
    for city, facilities in current.items():
        if not isinstance(facilities, dict):
            continue
        prev_city = previous.get(city, {})
        for facility, curr_count in facilities.items():
            if curr_count is None:
                continue
            prev_count = prev_city.get(facility)
            if prev_count is None:
                continue
            if curr_count > prev_count:
                increases.setdefault(city, []).append(
                    {"facility": facility, "prev": prev_count, "curr": curr_count}
                )
    return increases


def build_message(increases: dict) -> str:
    """増加情報から LINE 通知メッセージを組み立てる。"""
    lines = ["🍼 保育園空き情報更新", ""]
    for city, items in increases.items():
        lines.append(f"【{city}】")
        for item in items:
            lines.append(f"- {item['facility']}: {item['prev']}→{item['curr']}")
        lines.append("")
    return "\n".join(lines).rstrip()


def main() -> None:
    print("[main] 保育園空き状況チェック開始")

    # 前回データ読み込み
    previous = load_previous()
    print(f"[main] 前回データ読み込み完了。市数: {len(previous)}")

    # 各市のスクレイピング
    current = {}
    for city_name, scraper in CITIES.items():
        print(f"\n[main] {city_name} の処理を開始...")
        try:
            result = scraper.scrape()
            current[city_name] = result
            print(f"[main] {city_name} 完了。施設数: {len(result)}")
        except Exception as e:
            print(f"[main] {city_name} でエラーが発生しました: {e}")
            current[city_name] = {}

    # 増加検出
    increases = detect_increases(previous, current)

    if increases:
        message = build_message(increases)
        print(f"\n[main] 空き増加を検出しました:\n{message}")
        notify.send_message(message)
    else:
        print("\n[main] 空き数に変化はありませんでした。")

    # データ保存
    save_current(current)

    # 全市データを出力
    print("\n[main] === 現在の空き状況 ===")
    print(json.dumps(current, indent=2, ensure_ascii=False))
    print("[main] 処理完了")


if __name__ == "__main__":
    main()
