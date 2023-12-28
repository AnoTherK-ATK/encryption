import numpy as np
import cv2
from subprocess import call
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from sys import argv
from moviepy.editor import *
key = []

def logistic(r, x, size):
    for i in range(size):
        x = r * x * (1 - x)
        key.append((int(x * 10000) % 256))

def enc(filename):
    r = 4
    x = 0.54321
    vid = cv2.VideoCapture(filename)
    success = True
    cnt = 0
    fps = vid.get(cv2.CAP_PROP_FPS)
    res = [int(vid.get(cv2.CAP_PROP_FRAME_WIDTH)), int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))]
    audio = filename.split('.')[0]+".mp3"
    call(["ffmpeg", "-i", filename, "-vn", "-q:a", "0", "-map", "a",filename.split('.')[0]+".mp3"])
    logistic(r, x, int(vid.get(cv2.CAP_PROP_FRAME_COUNT)))
    print(str(int(vid.get(cv2.CAP_PROP_FRAME_COUNT))) + " frames")
    
    output = cv2.VideoWriter(filename.split('.')[0] + "_xor.mkv", cv2.VideoWriter_fourcc(*"FFV1"), fps, res)
    while success:
        success, image = vid.read() 
        if not success:
            break
        #image = np.array(image)
        image = np.bitwise_xor(image, key[cnt % len(key)])
        #image = Image.fromarray(image)
        cv2.imwrite("frames/output%d.png" % cnt ,np.array(image))
        output.write(image)
        cnt += 1
    output.release()
    call(["ffmpeg", "-i", filename.split('.')[0] + "_xor.mkv", "-i", audio, "-c:v", "copy", "-c:a", "aac", filename.split('.')[0] + "_xorhq.mkv"])
    return str(filename.split('.')[0] + "_xorhq.mkv")

def encAES(filename, enc_filename, output_filename):
    fkey = open(enc_filename, 'rb')
    akey = fkey.read()
    cipher = AES.new(akey, AES.MODE_CBC)
    f = open(filename, 'rb')
    data = f.read()
    ct_bytes = cipher.encrypt(pad(data, AES.block_size))
    fo = open(output_filename, 'wb')
    fo.write(cipher.iv)
    fo.write(ct_bytes)

encAES(enc(argv[1]), argv[2], argv[3])

