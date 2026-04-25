import re
from io import BytesIO
from urllib.parse import urljoin

import pdfplumber
import requests
from bs4 import BeautifulSoup

# 1歳児クラスを示すキーワード
AGE_KEYWORDS = ["1歳児", "１歳児", "1歳", "１歳", "1才", "１才"]


def fetch_pdf_urls(page_url: str) -> list:
    """ページHTMLを取得し、.pdf へのリンクURLをすべて返す。相対URLは絶対URLに変換する。"""
    try:
        response = requests.get(page_url, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"[base] ページ取得エラー ({page_url}): {e}")
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    pdf_urls = []
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        if href.lower().endswith(".pdf"):
            absolute_url = urljoin(page_url, href)
            pdf_urls.append(absolute_url)

    return pdf_urls


def download_pdf(pdf_url: str):
    """PDFをダウンロードして bytes で返す。エラー時は None を返す。"""
    try:
        response = requests.get(pdf_url, timeout=30)
        response.raise_for_status()
        return response.content
    except requests.RequestException as e:
        print(f"[base] PDFダウンロードエラー ({pdf_url}): {e}")
        return None


def _extract_facility_name_from_row(row: list) -> str:
    """テーブル行から施設名を推定する。最初の非空セルを施設名とする。"""
    for cell in row:
        if cell and isinstance(cell, str):
            text = cell.strip()
            # 年齢キーワードを含まないセルを施設名候補とする
            if text and not any(kw in text for kw in AGE_KEYWORDS):
                return text
    return "施設名不明"


def _first_number_in_row(row: list):
    """行のセルから最初に見つかった数値を返す。見つからない場合は None。"""
    for cell in row:
        if cell is not None:
            text = str(cell).strip()
            # 整数または「△」「×」のような記号を数値として扱う
            if re.fullmatch(r"\d+", text):
                return int(text)
    return None


def extract_vacancy_from_pdf(pdf_bytes: bytes) -> dict:
    """
    pdfplumber で PDF を解析し、1歳児クラスの施設名と空き数の辞書を返す。
    返値: {"施設名": 空き数(int) or None}
    """
    result = {}

    try:
        with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                # --- テーブルから抽出 ---
                tables = page.extract_tables()
                for table in tables:
                    if not table:
                        continue
                    # ヘッダー行から施設名列・空き数列を特定しようと試みる
                    for row in table:
                        if not row:
                            continue
                        row_text = " ".join(str(c) for c in row if c)
                        if any(kw in row_text for kw in AGE_KEYWORDS):
                            facility = _extract_facility_name_from_row(row)
                            vacancy = _first_number_in_row(row)
                            if facility in result:
                                # 同じ施設名が複数回出た場合は上書きしない
                                continue
                            result[facility] = vacancy

                # --- テキストから補完 ---
                if not result:
                    text = page.extract_text() or ""
                    # 「施設名 ... 1歳(児) ... 数値」のパターンを探す
                    lines = text.splitlines()
                    for line in lines:
                        if any(kw in line for kw in AGE_KEYWORDS):
                            # 行から数値を取得
                            numbers = re.findall(r"\d+", line)
                            vacancy = int(numbers[0]) if numbers else None
                            # 施設名を簡易的に取得（行の先頭部分を使用）
                            parts = re.split(r"[\s　]+", line.strip())
                            facility = parts[0] if parts else "施設名不明"
                            if not facility:
                                facility = "施設名不明"
                            result[facility] = vacancy

    except Exception as e:
        print(f"[base] PDF解析エラー: {e}")

    return result
