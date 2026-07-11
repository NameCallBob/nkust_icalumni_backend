import base64
import six
import uuid
import os
import logging
from django.core.files.base import ContentFile
from rest_framework import serializers
from django.conf import settings

logger = logging.getLogger(__name__)

# [資安修補 INFO-2] 圖片上傳的型別白名單與大小上限（可由 settings 覆寫）
ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
MAX_IMAGE_UPLOAD_SIZE = getattr(settings, 'MAX_IMAGE_UPLOAD_SIZE', 5 * 1024 * 1024)  # 預設 5MB


class Base64ImageField(serializers.ImageField):
    """
    處理通過原始 base64 編碼圖像數據的圖像上傳的 Django REST framework 字段。
    """
    def to_internal_value(self, data):
        # 檢查是否為 None 或空字串
        if data is None or data == '':
            return None

        # 檢查是否為 base64 字串
        if isinstance(data, six.string_types):
            # 檢查 base64 字串是否為 "data:" 格式
            if 'data:' in data and ';base64,' in data:
                # 從 base64 內容中分離標頭
                header, data = data.split(';base64,')
                logger.debug(f"解析 base64 圖片，標頭: {header}")
            else:
                logger.warning("收到的圖片資料沒有標準 base64 標頭")

            # 嘗試解碼檔案，如果失敗，則引發錯誤
            try:
                decoded_file = base64.b64decode(data)
                logger.debug(f"成功解碼 base64 圖片，大小: {len(decoded_file)} bytes")
            except Exception as e:
                logger.error(f"圖片解碼失敗: {str(e)}")
                self.fail('invalid_image')

            # [資安修補 INFO-2] 大小上限，避免超大檔案造成 DoS / 佔滿磁碟
            if len(decoded_file) > MAX_IMAGE_UPLOAD_SIZE:
                raise serializers.ValidationError(
                    f"圖片大小不能超過 {MAX_IMAGE_UPLOAD_SIZE // (1024 * 1024)}MB，請壓縮後再上傳"
                )

            # [資安修補 INFO-2] 以內容嗅探確認確實為允許的圖片格式（不信任前端副檔名）
            sniff_ext = self.get_file_extension(str(uuid.uuid4())[:12], decoded_file)
            if sniff_ext not in ALLOWED_IMAGE_EXTENSIONS:
                raise serializers.ValidationError(
                    "不支援的圖片格式，僅允許 JPG、PNG、GIF、WEBP"
                )

            # 生成檔案名稱（隨機 uuid，避免可預測路徑）
            file_name = str(uuid.uuid4())[:12]  # 12 個字符足夠用作檔案名稱
            complete_file_name = f"{file_name}.{sniff_ext}"
            logger.debug(f"生成檔案名稱: {complete_file_name}")

            # 從解碼的數據創建檔案
            data = ContentFile(decoded_file, name=complete_file_name)
            
            # 記錄檔案資訊
            logger.debug(f"已創建 ContentFile 對象: 名稱={data.name}, 大小={data.size} bytes")
            
            # 預期的檔案位置
            expected_path = os.path.join(settings.MEDIA_ROOT, data.name)
            logger.debug(f"預期檔案將被保存到: {expected_path}")
            
            # 檢查目錄是否存在
            directory = os.path.dirname(expected_path)
            if not os.path.exists(directory):
                try:
                    os.makedirs(directory, exist_ok=True)
                    logger.info(f"已創建目錄: {directory}")
                except Exception as e:
                    logger.error(f"無法創建目錄 {directory}: {str(e)}")

        return super(Base64ImageField, self).to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):
        # 使用 imghdr 庫依「實際內容」判斷圖片類型（不信任前端宣稱的副檔名）
        import imghdr
        extension = imghdr.what(file_name, decoded_file)
        extension = "jpg" if extension == "jpeg" else extension

        # imghdr 不認得 WEBP，手動以檔頭辨識（RIFF....WEBP）
        if extension is None and decoded_file[:4] == b'RIFF' and decoded_file[8:12] == b'WEBP':
            extension = "webp"

        # [資安修補 INFO-2] 無法辨識為合法圖片時回傳 None（呼叫端會拒絕），不再預設成 'jpg'
        if extension is None:
            logger.warning("無法確定圖片類型，拒絕此上傳")
        return extension