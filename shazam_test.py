from client_shazam import ShazamApi as rapidapi
import asyncio
from shazamio import Shazam, Serialize    
from mysecrets import shazam_api_key
import logging

logging.basicConfig(filename='shaztest.log', encoding='utf-8', level=logging.DEBUG)

async def main(loop):
    
    # audio_source = 'https://stream-relay-geo.ntslive.net/stream'
    audio_source = 'https://fm.chunt.org/stream'
    # audio_source = "https://doyouworld.out.airtime.pro/doyouworld_a"
    # audio_source = "https://kioskradiobxl.out.airtime.pro/kioskradiobxl_a"
    
    api_rapid = rapidapi(loop, shazam_api_key)
    api_shazamio = Shazam()
    while True:
        try:
            payload_from_rapid = await api_rapid._get(audio_source)
            #out_shazamio = await api_shazamio.recognize_song(audio_source)
            out_rapidapi = await api_rapid._post(payload_from_rapid)
            #out_rapidapi = await api_rapid._get(audio_source)
            out_shazamio = await api_shazamio.recognize_song(payload_from_rapid)
            
            #print('rapidapi')
            #print(out_rapidapi)
            #print('shazamio')
            #print(out_shazamio)

            print('short version')
            if out_shazamio['matches']:
                print(out_shazamio['track']['title'] + " " + out_shazamio['track']['subtitle'])
            else:
                print('no shazamio match')
                
            if out_rapidapi['matches']:
                print(out_rapidapi['track']['title'] + " " + out_rapidapi['track']['subtitle'])
            else:
                print('no rapid match')
            #serialized = Serialize.full_track(out_shazamio)
            #print(serialized)
            

            with open("idlog_shazamio.txt", 'a') as f:
                f.write(str(out_shazamio) + '\n')
            with open("idlog_rapidapi.txt", 'a') as f:
                f.write(str(out_rapidapi) + '\n')

            if out_shazamio['matches'] and out_rapidapi['matches']:
                if out_rapidapi['track']['title'] == out_shazamio['track']['title']:

                    print("match")
                    with open("idlog_matches.txt", 'a') as f:
                        f.write(str(printcurrenttime()) + " " + out_rapidapi['track']['title'] + " " + out_rapidapi['track']['subtitle'] + '\n')
            else:
                with open("idlog_shazamio_nomatches.txt", 'a') as f:
                    
                    if out_rapidapi['matches']:
                        f.write(str(printcurrenttime())  + " " +  out_rapidapi['track']['title'] + " " + out_rapidapi['track']['subtitle'] + " vs "  + "shazamapi no match" + '\n')
                    elif out_shazamio['matches']:
                        f.write(str(printcurrenttime())  + " " +  "rapidapi no match" + " vs "  + out_shazamio['track']['title'] + " " + out_shazamio['track']['subtitle'] + '\n')
                    else:
                        f.write(str(printcurrenttime())  + " " +  out_rapidapi['matches'] + " vs "  + out_shazamio['matches'] + '\n')
        except Exception as e:
            logging.error(e)

        await asyncio.sleep(180)


def printcurrenttime():
    import datetime
    now = datetime.datetime.now()
    #print ("Current date and time : ")
    return (now.strftime("%Y-%m-%d %H:%M:%S"))

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
