from logging.handlers import TimedRotatingFileHandler
import os

# 自定義壓縮處理器
class CompressedTimedRotatingFileHandler(TimedRotatingFileHandler):
    def doRollover(self):
        super().doRollover()
        # 自動壓縮舊日誌
        for log_file in self.getFilesToDelete():
            self.compress_log_file(log_file)

    def compress_log_file(self, log_file):
        if not log_file.endswith('.gz'):  # 防止重複壓縮
            import gzip
            with open(log_file, 'rb') as f_in:
                with gzip.open(f"{log_file}.gz", 'wb') as f_out:
                    f_out.writelines(f_in)
            os.remove(log_file)  # 刪除未壓縮的日誌文件
