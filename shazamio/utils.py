import pathlib
from enum import Enum
from io import BytesIO
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import aiofiles
import aiohttp
from aiohttp import ContentTypeError
from pydub import AudioSegment

from shazamio.exceptions import FailedDecodeJson
from shazamio.schemas.artists import ArtistQuery

SongT = Union[str, pathlib.Path, bytes, bytearray]
FileT = Union[str, pathlib.Path]


async def validate_json(
    resp: aiohttp.ClientResponse, content_type: str = "application/json"
) -> dict:
    try:
        return await resp.json(content_type=content_type)
    except ContentTypeError as e:
        bad_url = str(str(e).split(",")[2]).split("'")[1]
        raise FailedDecodeJson(f"Check args, URL is invalid\nURL- {bad_url}")







async def get_file_bytes(file: FileT) -> bytes:

    if file.startswith("http"):

        recording = BytesIO()
        chunk_count = 0

        async with aiohttp.ClientSession() as session:
            async with session.get(file) as resp:

                # record for 250 chunks
                while chunk_count < 250:

                    chunk = await resp.content.read(1024)
                    chunk_count += 1

                    if not chunk:
                        break

                    recording.write(chunk)

                recording.seek(0)

                return recording.read()
    else:
        async with aiofiles.open(file, mode="rb") as f:
            return await f.read()




async def get_song(data: SongT) -> Union[AudioSegment]:

    if isinstance(data, (str, pathlib.Path)):
        song_bytes = await get_file_bytes(file=data)

        if data.startswith("http"):
            sound = AudioSegment.from_file(BytesIO(song_bytes))

            sound = sound.set_channels(1)
            sound = sound.set_sample_width(2)
            sound = sound.set_frame_rate(44100)

            # return base64.b64encode(sound.raw_data)
            return sound
        else:
            return AudioSegment.from_file(BytesIO(song_bytes))

    if isinstance(data, (bytes, bytearray)):
        return AudioSegment.from_file(BytesIO(data))

    if isinstance(data, AudioSegment):
        return data


class QueryBuilder:
    def __init__(
        self,
        source: List[Union[str, Enum]],
    ):
        self.source = source

    def to_str(self) -> str:
        return ",".join(self.source)


class ArtistQueryGenerator:
    def __init__(
        self,
        source: Optional[ArtistQuery] = None,
    ):
        self.source = source

    def params(self) -> Dict[str, str]:
        return {
            "extend": QueryBuilder(source=self.source.extend or []).to_str(),
            "views": QueryBuilder(source=self.source.views or []).to_str(),
        }
