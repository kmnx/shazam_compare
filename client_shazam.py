import asyncio
import aiohttp
from io import BytesIO
from pydub import AudioSegment

import base64
import mysecrets

shazam_api_key = mysecrets.shazam_api_key


class ShazamApi:
    def __init__(self, loop, api_key):

        self.api_url = "https://shazam.p.rapidapi.com/"
        self.api_host = "shazam.p.rapidapi.com"
        self.headers = {
            "content-type": "text/plain",
            "x-rapidapi-host": self.api_host,
            "x-rapidapi-key": shazam_api_key,
        }

    async def _get(self, streamsource, session=None):
        """
        get from shazam api
        :param query
        :return: API response
        """
        starttime = asyncio.get_event_loop().time()
        recording = BytesIO()

        sound = ""
        out = ""
        if session == None:
            session = aiohttp.ClientSession()
        async with session as session:
            try:
                async with session.get(streamsource) as response:
                    print("started recording")
                    # added chunk_count to counter initial data burst of some stations
                    chunk_count = 0
                    #while asyncio.get_event_loop().time() < (starttime + 4):
                    while chunk_count < 250:
                        chunk = await response.content.read(1024)
                        chunk_count += 1
                        #print("written chunk ", chunk_count)
                        if not chunk:
                            break

                        recording.write(chunk)
                        # some stations send lots of buffered audio on connect which might already be too much for shazam
                        # so we break at 250 chunks. 4s of 256kbit stream are about 213 chunks
                        #if chunk_count > 250:
                        #    break

                    recording.seek(0)

                    sound = AudioSegment.from_file(recording)
                    sound = sound.set_channels(1)
                    sound = sound.set_sample_width(2)
                    sound = sound.set_frame_rate(44100)
            except aiohttp.client_exceptions.ClientConnectorError as e:
                print("there was a ClientConnectorError")
                print(e)
            if sound:
                payload = base64.b64encode(sound.raw_data)
                async with session.post(
                    "https://shazam.p.rapidapi.com/songs/v2/detect",
                    data=payload,
                    headers=self.headers,
                ) as response:
                    try:
                        out = await response.json()
                    except Exception as e:
                        print(e)
            else:
                out = ""
                print("no audio")
            return out


async def loopy(loop):
    n = 1
    while True:
        print("woop", n)
        n += 1
        await asyncio.sleep(1)


async def main(loop):

    # audio_source = 'https://stream-relay-geo.ntslive.net/stream'
    # audio_source = 'https://fm.chunt.org/stream'
    audio_source = "https://doyouworld.out.airtime.pro/doyouworld_a"
    # audio_source = "https://kioskradiobxl.out.airtime.pro/kioskradiobxl_a"
    asyncio.ensure_future(loopy(loop))
    api = ShazamApi(loop, shazam_api_key)
    out = await api._get(audio_source)
    print(out)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
