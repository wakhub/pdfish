# テーブルを扱う

テーブルを扱うには [camelot](https://camelot-py.readthedocs.io/en/master/) が利用できる。

## 注意点

- 依存関係で PyPDF2 の最新版を入れると [DeprecationError が発生してしまう](https://stackoverflow.com/questions/74939758/camelot-deprecationerror-pdffilereader-is-deprecated)ので、`PyPDF2<3.0` をインストールする。
- `ImportError: libGL.so.1` が出た場合は `apt install libgl1` 等で対処。
- ページを跨ぐテーブルはうまく扱えない