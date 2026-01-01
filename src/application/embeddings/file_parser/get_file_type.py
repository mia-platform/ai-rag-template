from enum import Enum

from fastapi import UploadFile

from src.constants import (
    GZIP_COMPRESSED_CONTENT_TYPE,
    GZIP_CONTENT_TYPE,
    GZIP_EXTENSION,
    MD_CONTENT_TYPE,
    MD_EXTENSION,
    MDX_EXTENSION,
    PDF_CONTENT_TYPE,
    PDF_EXTENSION,
    TAR_CONTENT_TYPE,
    TAR_EXTENSION,
    TEXT_CONTENT_TYPE,
    TEXT_EXTENSION,
    ZIP_COMPRESSED_CONTENT_TYPE,
    ZIP_CONTENT_TYPE,
    ZIP_EXTENSION,
)


class FileType(Enum):
    TEXT = "text"
    PDF = "pdf"
    ZIP = "zip"
    TAR = "tar"
    GZIP = "gzip"


CONTENT_TYPE_MAP = {
    TEXT_CONTENT_TYPE: FileType.TEXT,
    MD_CONTENT_TYPE: FileType.TEXT,
    PDF_CONTENT_TYPE: FileType.PDF,
    ZIP_CONTENT_TYPE: FileType.ZIP,
    TAR_CONTENT_TYPE: FileType.TAR,
    ZIP_COMPRESSED_CONTENT_TYPE: FileType.ZIP,
    GZIP_CONTENT_TYPE: FileType.GZIP,
    GZIP_COMPRESSED_CONTENT_TYPE: FileType.GZIP,
}

EXTENSION_TYPE_MAP = {
    TEXT_EXTENSION: FileType.TEXT,
    MD_EXTENSION: FileType.TEXT,
    MDX_EXTENSION: FileType.TEXT,
    PDF_EXTENSION: FileType.PDF,
    ZIP_EXTENSION: FileType.ZIP,
    TAR_EXTENSION: FileType.TAR,
    GZIP_EXTENSION: FileType.GZIP,
}


def get_file_type(file: UploadFile):
    content_type = file.content_type
    file_extension = file.filename.split(".")[-1]

    return CONTENT_TYPE_MAP.get(content_type, None) or EXTENSION_TYPE_MAP.get(file_extension, None)
