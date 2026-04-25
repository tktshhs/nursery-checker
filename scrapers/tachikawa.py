from scrapers.base import fetch_pdf_urls, download_pdf, extract_vacancy_from_pdf

PAGE_URL = "https://www.city.tachikawa.lg.jp/kosodate/m-kosodate/1004946/1005097/1005184.html"


def scrape() -> dict:
    """立川市の保育園1歳児クラス空き情報を取得する。"""
    print(f"[tachikawa] ページを取得中: {PAGE_URL}")
    pdf_urls = fetch_pdf_urls(PAGE_URL)

    if not pdf_urls:
        print("[tachikawa] PDFが見つかりませんでした。")
        return {}

    print(f"[tachikawa] {len(pdf_urls)} 件のPDFを検出。最初のPDFを処理します: {pdf_urls[0]}")
    pdf_bytes = download_pdf(pdf_urls[0])
    if pdf_bytes is None:
        print("[tachikawa] PDFのダウンロードに失敗しました。")
        return {}

    print("[tachikawa] PDFを解析中...")
    result = extract_vacancy_from_pdf(pdf_bytes)
    print(f"[tachikawa] 取得結果: {result}")
    return result
