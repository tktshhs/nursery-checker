import re
from io import BytesIO
from urllib.parse import urljoin

import pdfplumber
import requests
from bs4 import BeautifulSoup

# 1歳児クラスを示すキーワード
AGE_KEYWORDS = ["1歳児", "１歳児", "1歳", "１歳", "1才", "１才"]

# 全角→半角変換テーブル
_ZEN_TO_HAN = str.maketrans("０１２３４５６７８９", "0123456789")
