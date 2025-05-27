# IC_alumni/log/rotating.py
import gzip
import shutil
from logging.handlers import TimedRotatingFileHandler

class CompressedTimedRotatingFileHandler(TimedRotatingFileHandler):
    def doRollover(self):
        super().doRollover()
        # 壓縮舊檔案
        if self.backupCount > 0:
            log_dir = os.path.dirname(self.baseFilename)
            for filename in os.listdir(log_dir):
                if filename.startswith(os.path.basename(self.baseFilename)) and not filename.endswith('.gz'):
                    full_path = os.path.join(log_dir, filename)
                    with open(full_path, 'rb') as f_in:
                        with gzip.open(full_path + '.gz', 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    os.remove(full_path)

