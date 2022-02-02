import utils.scripts as scripts
import struct #parsing
import zlib #decompressing
import matplotlib.pyplot as plt
import numpy as np

img_to_open=open('resources\\basn6a08.png', 'rb')

png_signature = b'\x89PNG\r\n\x1a\n' #b is for byte string.


 
rules=scripts.IHDR_rule_definition(6,8,0,0,0)

if (img_to_open.read(len(png_signature)) != png_signature): #reading the first 8 byte(len()) og img to open and checking if his signature is same of png.
    raise Exception ('Invalid Png Signature')

chunks=[]
while True:
    chunk_type, chunk_data = scripts.chunk_reader(img_to_open)
    chunks.append((chunk_type, chunk_data))
    if chunk_type == b'IEND':
        break

width, height, bitd, colort, compm, filterm, interlacem=scripts.IHDR_sanity_check(rules,chunks)


IDAT_data = b''.join(chunk_data for chunk_type, chunk_data in chunks if chunk_type == b'IDAT') #getting all the data of different idat.
IDAT_data = zlib.decompress(IDAT_data)

#Reconstructions
Recon = []

bytesPerPixel = 4
stride = width * bytesPerPixel

#R IS THE SCANLINE INDEX




Recon=scripts.Paeth_ReconstructionLoop(IDAT_data,height,stride,Recon,bytesPerPixel)


plt.imshow(np.array(Recon).reshape((height, width, 4)))
plt.show()