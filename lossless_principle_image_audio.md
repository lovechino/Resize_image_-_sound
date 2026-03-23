# Nguyên lý Lossless trong xử lý ảnh và audio

## 1. Khái niệm

**Lossless (nén không mất dữ liệu)** là phương pháp nén dữ liệu mà sau
khi giải nén, dữ liệu thu được **giống 100% dữ liệu ban đầu**. Không có
thông tin nào bị mất.

Ứng dụng phổ biến: - Ảnh: PNG, GIF, TIFF - Audio: FLAC, ALAC, WAV

------------------------------------------------------------------------

# 2. Nguyên lý chung của Lossless Compression

Ý tưởng chính là **tìm sự dư thừa trong dữ liệu** và mã hoá lại theo
cách ngắn gọn hơn.

Các loại dư thừa:

## 2.1 Statistical Redundancy

Một số giá trị xuất hiện nhiều hơn giá trị khác.

Ví dụ: AAAABBBCC

Có thể nén thành: (4,A) (3,B) (2,C)

------------------------------------------------------------------------

## 2.2 Spatial Redundancy (Ảnh)

Pixel gần nhau thường giống nhau.

Ví dụ:

120 121 121 122

Có thể lưu dưới dạng sai số:

120 +1 0 +1

Sai số nhỏ sẽ nén tốt hơn.

------------------------------------------------------------------------

## 2.3 Temporal Redundancy (Audio)

Các mẫu âm thanh gần nhau thường thay đổi nhỏ.

Ví dụ sample:

1000 1002 1003 1005

Lưu:

1000 +2 +1 +2

------------------------------------------------------------------------

# 3. Các thuật toán Lossless phổ biến

## 3.1 Run Length Encoding (RLE)

Dùng khi dữ liệu lặp nhiều.

Ví dụ:

AAAAAAABBBBBCCCC

Nén thành:

(7,A) (5,B) (4,C)

------------------------------------------------------------------------

## 3.2 Huffman Coding

Giá trị xuất hiện nhiều sẽ có mã ngắn hơn.

Ví dụ:

  Value   Code
  ------- ------
  A       0
  B       10
  C       11

------------------------------------------------------------------------

## 3.3 LZ Compression

Tìm pattern lặp lại trong dữ liệu.

Ví dụ:

ABCABCABC

Có thể lưu:

ABC (repeat 3)

Các biến thể phổ biến:

-   LZ77
-   LZ78
-   DEFLATE

PNG sử dụng DEFLATE.

------------------------------------------------------------------------

# 4. Lossless trong xử lý ảnh

Các định dạng phổ biến:

-   PNG
-   GIF
-   TIFF (lossless mode)

Các bước thường dùng:

1.  Prediction (dự đoán pixel)
2.  Tính sai số (residual)
3.  Entropy coding (Huffman / LZ)

------------------------------------------------------------------------

# 5. Lossless trong xử lý Audio

Các định dạng phổ biến:

-   FLAC
-   ALAC
-   WAV

Quy trình:

1.  Predict sample
2.  Tính residual
3.  Nén residual bằng Huffman hoặc Rice Coding

------------------------------------------------------------------------

# 6. So sánh Lossless và Lossy

  Đặc điểm      Lossless    Lossy
  ------------- ----------- -----------
  Mất dữ liệu   Không       Có
  Khôi phục     100%        Không
  Tỉ lệ nén     Thấp hơn    Cao hơn
  Ví dụ         PNG, FLAC   JPEG, MP3

------------------------------------------------------------------------

# 7. Tóm tắt

Lossless compression hoạt động theo 3 bước:

1.  Phát hiện pattern hoặc dự đoán dữ liệu
2.  Chuyển dữ liệu thành sai số nhỏ
3.  Áp dụng entropy coding

Kết quả: - Giảm kích thước file - Không mất dữ liệu - Khôi phục chính
xác dữ liệu ban đầu
