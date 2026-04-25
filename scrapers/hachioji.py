from scrapers.base import fetch_pdf_urls, download_pdf, extract_vacancy_from_pdf

PAGE_URL = "https://www.city.hachioji.tokyo.jp/kurashi/kosodate/003/00091/008/p020411.html"


def scrape() -> dict:
    """八王子市の保育園1歳児クラス空き情報を取得する。"""
    print(f"[hachioji] ページを取得中: {PAGE_URL}")
    pdf_urls = fetch_pdf_urls(PAGE_URL)

    if not pdf_urls:
        print("[hachioji] PDFが見つかりませんでした。")
        return {}

    print(f"[hachioji] {len(pdf_urls)} 件のPDFを検出。最初のPDFを処理します: {pdf_urls[0]}")
    pdf_bytes = download_pdf(pdf_urls[0])
    if pdf_bytes is None:
        print("[hachioji] PDFのダウンロードに失敗しました。")
        return {}

    print("[hachioji] PDFを解析中...")
    result = extract_vacancy_from_pdf(pdf_bytes)
    print(f"[hachioji] 取得結果: {result}")
    return result
