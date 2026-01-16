# utils/logger_setup.py
# Modul untuk konfigurasi logging agar konsisten di seluruh proyek.

import logging
import os

def get_logger(name: str, log_dir: str = "logs"):
    """
    Mengkonfigurasi dan mengembalikan logger.
    
    Args:
        name (str): Nama logger.
        log_dir (str): Direktori untuk menyimpan file log.
        
    Returns:
        logging.Logger: Objek logger yang telah dikonfigurasi.
    """
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Menghindari penambahan handler duplikat
    logger = logging.getLogger(name)
    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    
    # Console Handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    
    # File Handler untuk Info
    info_path = os.path.join(log_dir, "info.log")
    fh_info = logging.FileHandler(info_path, encoding="utf-8")
    fh_info.setLevel(logging.INFO)
    fh_info.setFormatter(formatter)
    logger.addHandler(fh_info)

    # File Handler untuk Error
    error_path = os.path.join(log_dir, "error.log")
    fh_error = logging.FileHandler(error_path, encoding="utf-8")
    fh_error.setLevel(logging.ERROR)
    fh_error.setFormatter(formatter)
    logger.addHandler(fh_error)
    
    return logger
