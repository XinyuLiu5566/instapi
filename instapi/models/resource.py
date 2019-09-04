import io
import shutil
from pathlib import Path
from typing import (
    Any,
    Dict,
    Iterable,
    Optional,
    Union,
)
from urllib.parse import urlparse

import requests
from dataclasses import dataclass
from PIL import Image as PILImage

from instapi.models.base import BaseModel


@dataclass(frozen=True)
class Resource(BaseModel):
    """
    This class represents image or video, which contains in the post
    """
    url: str
    width: int
    height: int

    @property
    def filename(self) -> Path:
        """
        Return the name of image/video

        :return: path to file
        """
        *_, filename = urlparse(self.url).path.split('/')
        return Path(filename)

    def download(self, directory: Path = None, filename: Union[Path, str] = None) -> None:
        """
        Download image/video

        :param directory: path for storage file
        :param filename: name of file, which will be downloaded
        :return: None
        """
        filename = filename or self.filename

        if directory:
            into = directory / filename
        else:
            into = Path(filename)

        response = requests.get(self.url, stream=True)

        with into.open(mode='wb') as f:
            shutil.copyfileobj(response.raw, f)

    @classmethod
    def create_resources(
            cls,
            resources_data: Iterable[Dict[str, Any]],
            video: bool = True,
            image: bool = True,
    ) -> Iterable['Resources']:
        """
        Create a generator for iteration over images/videos, which contains in the resources_data

        :param resources_data: iterable with information about resources
        :param video: true - add videos, false - ignore videos
        :param image: true - add images, false - ignore images
        :return: generator with images/videos
        """
        for data in resources_data:
            if (video and cls.is_video_data(data)) or (image and cls.is_image_data(data)):
                resource = cls.from_data(data)

                if resource is not None:
                    yield resource

    @classmethod
    def from_data(cls, data: Dict[str, Any]) -> Optional['Resources']:
        """
        Create resource based on data fetched from api

        :param data: data from api
        :return: resource instance or None
        """
        if cls.is_video_data(data):
            return Video.create(data['video_versions'][0])
        elif cls.is_image_data(data):
            return Image.create(data['image_versions2']['candidates'][0])
        else:
            return None

    @staticmethod
    def is_video_data(data: Dict[str, Any]) -> bool:
        """
        Check if given data contains information about video resource

        :param data: resource data
        :return: is given data contains information about video resource
        """
        return 'video_versions' in data

    @staticmethod
    def is_image_data(data: Dict[str, Any]) -> bool:
        """
        Check if given data contains information about image resource

        :param data: resource data
        :return: is given data contains information about image resource
        """
        return 'video_versions' not in data and 'image_versions2' in data


@dataclass(frozen=True)
class Video(Resource):
    """
    This class represents video resource
    """


@dataclass(frozen=True)
class Image(Resource):
    """
    This class represents image resource
    """

    def preview(self) -> None:
        """
        Show preview of image

        :return: None
        """
        response = requests.get(self.url)
        image = io.BytesIO(response.content)
        img = PILImage.open(image)
        img.show()


Resources = Union[Image, Video]

__all__ = [
    'Resource',
    'Resources',
    'Video',
    'Image',
]
