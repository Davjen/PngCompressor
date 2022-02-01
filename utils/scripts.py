import zlib
import struct


def chunk_reader(f):
    #Returns (chunk_type,chunk_data)
    chunk_length, chunk_type = struct.unpack('>I4s', f.read(8)) #integer 4char(?)
    chunk_data = f.read(chunk_length)
    checksum = zlib.crc32(chunk_data, zlib.crc32(struct.pack('>4s', chunk_type)))
    chunk_crc, = struct.unpack('>I', f.read(4))
    if chunk_crc != checksum:
        raise Exception('chunk checksum failed {} != {}'.format(chunk_crc,
            checksum))
    return chunk_type, chunk_data


def IHDR_rule_definition(color_type,bit_depth,interlace_method,filter_method,compression_method):
    """Define your rules for support"""
    rule_def={"color_type":color_type,
                "bit_depth":bit_depth,
                "interlace_method":interlace_method,
                "filter_method":filter_method,
                "compression_method":compression_method}
    
    return rule_def
    
def IHDR_sanity_check(rules,chunk):
    """Given the rules check the sanity of the IHDR"""
    _, IHDR_data = chunk[0] # IHDR is always first chunk #_ insert the type, useless that's
    width, height, bitd, colort, compm, filterm, interlacem = struct.unpack('>IIBBBBB', IHDR_data) #INTEGER INTEGER BYTE BYTE BYTE ECC

    if colort != rules["color_type"]:
        raise Exception('we only support truecolor with alpha')
    if compm != rules["compression_method"]:
        raise Exception('invalid compression method')
    if filterm != rules["filter_method"]:
        raise Exception('invalid filter method')
    if bitd != rules["bit_depth"]:
        raise Exception('we only support a bit depth of 8')
    if interlacem != rules["interlace_method"]:
        raise Exception('we only support no interlacing')

    return width, height, bitd, colort, compm, filterm, interlacem

def PaethPredictor(a, b, c):
    p = a + b - c
    pa = abs(p - a)
    pb = abs(p - b)
    pc = abs(p - c)
    if pa <= pb and pa <= pc:
        Pr = a
    elif pb <= pc:
        Pr = b
    else:
        Pr = c
    return Pr

def __Recon_a(r, c,stride,bytesPerPixel,Recon):
    return Recon[r * stride + c - bytesPerPixel] if c >= bytesPerPixel else 0

def __Recon_b(r, c,stride,Recon):
    return Recon[(r-1) * stride + c] if r > 0 else 0

def __Recon_c(r, c,stride,bytesPerPixel,Recon):
    return Recon[(r-1) * stride + c - bytesPerPixel] if r > 0 and c >= bytesPerPixel else 0

def Paeth_ReconstructionLoop(IDAT_data,height,stride,Recon,bytesPerPixel):
    

    i = 0
    for r in range(height): # for each scanline
        filter_type = IDAT_data[i] # first byte of scanline is filter type
        i += 1
        for c in range(stride): # for each byte in scanline
            Filt_x = IDAT_data[i]
            i += 1
            if filter_type == 0: # None
                Recon_x = Filt_x
            elif filter_type == 1: # Sub
                Recon_x = Filt_x + __Recon_a(r,c,stride,bytesPerPixel,Recon)
            elif filter_type == 2: # Up
                Recon_x = Filt_x + __Recon_b(r,c,stride,Recon)
            elif filter_type == 3: # Average
                Recon_x = Filt_x + (__Recon_a(r,c,stride,bytesPerPixel,Recon) + __Recon_b(r,c,stride,Recon)) // 2
            elif filter_type == 4: # Paeth
                Recon_x = Filt_x + PaethPredictor(__Recon_a(r, c,stride,bytesPerPixel,Recon), __Recon_b(r, c,stride,Recon), __Recon_c(r, c,stride,bytesPerPixel,Recon))
            else:
                raise Exception('unknown filter type: ' + str(filter_type))
            Recon.append(Recon_x & 0xff) # truncation to byte
    return Recon
