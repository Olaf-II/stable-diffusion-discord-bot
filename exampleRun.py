import random
import requests
import json
import base64

prompt = "Discord bot for stable diffusion diffusing, logo"
url = 'http://127.0.0.1:7860/api/predict/'

def main():
    response = requests.post(url, json={"fn_index":13,"data":[f"{prompt}","","None","None",150,"Euler a",False,False,1,4,7,-1,-1,0,0,0,False,512,512,False,0.7,0,0,"None",False,False,None,"","Seed","","Nothing","",True,False,False,None,"",""],"session_hash":"hqp09fk5746"})
    jsonResponse = json.loads(b''.join(response))
    open('debug.txt', 'w').write(json.dumps(jsonResponse))
    base64Response = str((jsonResponse["data"])[0])[24:-2].encode()
    with open(f"./{prompt}.png", "wb") as fh:
        fh.write(base64.decodebytes(base64Response))

main()