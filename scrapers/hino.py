from scrapers.base import fetch_pdf_urls, download_pdf, extract_vacancy_from_pdf

PAGE_URL = "https://www.city.hino.lg.jp/kosodate/1028734/1029177/1029282/index.html"


def scrape() -> dict:
    """日野市の保育園1歳児クラス空き情報を取得する。"""
    print(f"[hino] ページを取得中: {PAGE_URL}")
    pdf_urls = fetch_pdf_urls(PAGE_URL)

    if not pdf_urls:
        print("[hino] PDFが見つかりませんでした。")
        return {}

    print(f"[hino] {len(pdf_urls)} 件のPDFを検出。最初のPDFを処理します: {pdf_urls[0]}")
    pdf_bytes = download_pdf(pdf_urls[0])
    if pdf_bytes is None:
        print("[hino] PDFのダウンロードに失敗しました。")
        return {}

    print("[hino] PDFを解析中...")
    result = extract_vacancy_from_pdf(pdf_bytes)
    print(f"[hino] 取得結果: {result}")
    return result
