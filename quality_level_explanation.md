# Asset Maximizer - Ý Nghĩa Của Từng Quality Level

Sau khi tính năng ép thu nhỏ ảnh (`max_width`) bị vô hiệu hóa trong Backend, cấu hình **Quality Level** chỉ thực hiện một việc duy nhất là can thiệp vào sức nén file (File Compression) của định dạng Ảnh và Âm thanh. 

Sự khác biệt thực tế giữa các level như sau:

### 1. High (Chất lượng cao - PC/Console)
- **Hình ảnh:** 
  - **JPG:** Nén ở mức độ cao (Quality: `85`).
  - **PNG:** Giảm màu tối ưu giữ lại `256 màu`. Gần như tương đồng bản gốc mắt thường khó phân biệt.
- **Âm thanh (MP3):** 
  - **Bitrate:** `192k` | **Sample Rate:** `44100Hz`
  - *Kết quả:* Giữ được toàn bộ dải băng tần âm thanh, nghe trên tai nghe và loa tốt.

### 2. Medium (Tiêu chuẩn - Trải nghiệm mặc định cho Mobile)
- **Hình ảnh:** 
  - **JPG:** Nén cân bằng (Quality: `70`). Dung lượng giảm đáng kể để nạp nhanh qua mạng nhưng vẫn đủ nét.
  - **PNG:** Ép xuống còn `64 màu`. Cực kỳ nhẹ cho các khối ảnh sprite/tilemap đồ họa 2D.
- **Âm thanh (MP3):** 
  - **Bitrate:** `128k` | **Sample Rate:** `44100Hz`
  - *Kết quả:* Tiêu chuẩn phổ thông nhất của MP3. File nhẹ hơn khoảng 30% mà nghe qua loa điện thoại khác biệt không đáng kể.

### 3. Low (Ép nén mạnh nhất - Dành cho Web Game tối ưu đường truyền)
- **Hình ảnh:** 
  - **JPG:** Nén ở mức gắt (Quality: `50`). Chắc chắn sẽ làm ảnh bị mờ hoặc xuất hiện các khối hạt nhiễu nhỏ (artifacts).
  - **PNG:** Ép kiệt xuống `32 màu`. Các vùng có màu gradient (chuyển sắc) có thể sẽ bị rạn ranh giới hoặc mảng khối (banding).
- **Âm thanh (MP3):** 
  - **Bitrate:** `32k` | **Sample Rate:** `16000Hz`
  - *Kết quả:* Âm thanh nghe bị đục, mất hoàn toàn chất lượng dải bass/treble, tạo cảm giác giống đài radio kiểu cũ (lo-fi). File âm thanh cực kì nhẹ (có thể giảm tới 80% dung lượng bản gốc).
