from scrapers.base import fetch_pdf_urls, download_pdf, extract_vacancy_from_pdf

PAGE_URL = "https://www.city.fuchu.tokyo.jp/kosodate/shussan/hoikujo/ukeireyotei.html"


def scrape() -> dict:
    """府中市の保育園1歳児クラス空き情報を取得する。"""
    print(f"[fuchu] ページを取得中: {PAGE_URL}")
    pdf_urls = fetch_pdf_urls(PAGE_URL)

    if not pdf_urls:
        print("[fuchu] PDFが見つかりませんでした。")
        return {}

    print(f"[fuchu] {len(pdf_urls)} 件のPDFを検出。最初のPDFを処理します: {pdf_urls[0]}")
    pdf_bytes = download_pdf(pdf_urls[0])
    if pdf_bytes is None:
        print("[fuchu] PDFのダウンロードに失敗しました。")
        return {}

    print("[fuchu] PDFを解析中...")
    result = extract_vacancy_from_pdf(pdf_bytes)
    print(f"[fuchu] 取得結果: {result}")
    return result
