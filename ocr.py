import logging
from PIL import Image, ImageOps
# from tesserocr import PyTessBaseAPI, OEM, PSM

ascii_table = [[0]] * 128
ascii_table[33] = [524080, 524080]
ascii_table[35] = [768, 25344, 25392, 25584, 32640, 260864, 484096, 25456, 28640, 65280, 516864, 418560, 25344, 24576]
ascii_table[37] = [122880, 258048, 399360, 264192, 399408, 258240, 123264, 1536, 2048, 12288, 50112, 100320, 396336, 2064, 3120, 2016, 960]
ascii_table[38] = [1920, 4064, 130144, 260208, 473136, 400432, 396848, 395104, 197600, 448, 2016, 3952, 3120, 16]
ascii_table[39] = [507904, 507904]
ascii_table[40] = [16320, 131064, 491582, 262146]
ascii_table[41] = [262146, 491582, 131064, 16320]
ascii_table[42] = [67584, 36864, 36864, 24576, 523776, 24576, 36864, 36864, 67584]
ascii_table[43] = [1536, 1536, 1536, 1536, 1536, 65520, 65520, 1536, 1536, 1536, 1536, 1536]
ascii_table[44] = [6, 60, 56]
ascii_table[45] = [1536, 1536, 1536, 1536, 1536]
ascii_table[46] = [48, 48]
ascii_table[47] = [24, 248, 2032, 16128, 260096, 507904, 393216]
ascii_table[48] = [32512, 131008, 229600, 393264, 393264, 393264, 393264, 229600, 131008, 32512]
ascii_table[49] = [196608, 196656, 393264, 393264, 524272, 524272, 48, 48, 48]
#ascii_table[50] = [196720, 393456, 393712, 393648, 395056, 396848, 465968, 260144, 127024]
ascii_table[50] = [196720, 393456, 393712, 393648, 395056, 396848, 465968, 260144, 122928]
ascii_table[51] = [196704, 393264, 393264, 399408, 399408, 399408, 473136, 257120, 124896, 960]
ascii_table[52] = [896, 1920, 7552, 12672, 57728, 229760, 393600, 524272, 524272, 384, 384]
ascii_table[53] = [96, 522288, 520240, 405552, 405552, 405552, 407648, 401376, 3968]
ascii_table[54] = [32640, 131040, 248928, 198704, 399408, 399408, 399408, 400496, 200672, 1984]
ascii_table[55] = [393216, 393216, 393216, 393232, 393456, 395232, 409344, 522240, 507904, 393216]
ascii_table[56] = [115648, 258016, 474224, 399408, 399408, 399408, 399408, 474224, 258016, 115648]
ascii_table[57] = [126976, 260192, 465968, 396336, 396336, 396336, 395360, 203232, 262080, 65280]
ascii_table[58] = [12336, 12336]
ascii_table[60] = [3584, 3584, 3584, 7936, 6912, 6912, 12672, 12672, 12672, 24768, 24768, 24768, 49248]
ascii_table[61] = [6528, 6528, 6528, 6528, 6528, 6528, 6528, 6528, 6528, 6528, 6528, 6528, 6528]
ascii_table[62] = [49248, 24768, 24768, 24768, 12672, 12672, 12672, 6912, 6912, 7936, 3584, 3584, 3584]
ascii_table[64] = [8064, 32736, 57456, 114744, 229404, 200460, 466822, 408006, 405702, 405702, 399750, 409548, 212940, 196824, 229760, 115584, 65280, 15872]
ascii_table[65] = [16, 240, 2016, 16256, 63872, 516480, 459136, 516480, 63872, 16256, 2016, 240, 16]
ascii_table[66] = [524272, 524272, 399408, 399408, 399408, 399408, 473136, 261232, 124896, 960]
ascii_table[67] = [32512, 65408, 246240, 196704, 458864, 393264, 393264, 393264, 393264, 393264, 393264, 196704]
ascii_table[68] = [524272, 524272, 393264, 393264, 393264, 393264, 393264, 458864, 196704, 246240, 131008, 32512]
ascii_table[69] = [524272, 524272, 399408, 399408, 399408, 399408, 399408, 399408, 399408]
ascii_table[70] = [524272, 524272, 399360, 399360, 399360, 399360, 399360, 393216]
ascii_table[71] = [32512, 130944, 246208, 196704, 458864, 393264, 393264, 393264, 396336, 396336, 396320, 200672, 4032]
ascii_table[72] = [524272, 524272, 6144, 6144, 6144, 6144, 6144, 6144, 6144, 524272, 524272]
ascii_table[74] = [3, 3, 7, 524286, 524284]
ascii_table[75] = [524272, 524272, 15360, 32256, 59136, 115584, 229824, 458976, 393328, 262192, 16]
ascii_table[76] = [524272, 524272, 48, 48, 48, 48, 48, 48, 48]
ascii_table[77] = [524272, 524272, 458752, 516096, 64512, 8064, 896, 8064, 64512, 516096, 458752, 524272, 524272]
ascii_table[78] = [524272, 524272, 491520, 253952, 63488, 15872, 3968, 960, 240, 524272, 524272]
ascii_table[79] = [32512, 65408, 246240, 196704, 458864, 393264, 393264, 393264, 393264, 458864, 196704, 246240, 65408, 32512]
ascii_table[80] = [524272, 524272, 396288, 396288, 396288, 396288, 465920, 260096, 126976]
ascii_table[81] = [32512, 65408, 246240, 196704, 458864, 393264, 393264, 393264, 393272, 458876, 196718, 246214, 130944, 32512]
ascii_table[82] = [524272, 524272, 399360, 399360, 399360, 400384, 474624, 259968, 123872, 112, 16]
ascii_table[83] = [122976, 258096, 473136, 399408, 399408, 399408, 396336, 396400, 198624, 960]
ascii_table[84] = [393216, 393216, 393216, 393216, 393216, 524272, 524272, 393216, 393216, 393216, 393216, 393216]
ascii_table[85] = [524160, 524256, 224, 48, 48, 48, 48, 48, 224, 524256, 524160]
ascii_table[86] = [262144, 491520, 258048, 32256, 3968, 1008, 112, 1008, 3968, 32256, 258048, 491520, 262144]
ascii_table[87] = [393216, 516096, 130816, 8176, 496, 2032, 32704, 522240, 491520, 491520, 522240, 32704, 2032, 496, 8176, 130560, 516096, 393216]
ascii_table[88] = [16, 262192, 458992, 491968, 124800, 32256, 15872, 65280, 115648, 491760, 393328, 262160]
ascii_table[89] = [262144, 393216, 491520, 122880, 61440, 16368, 16368, 61440, 122880, 491520, 393216, 262144]
ascii_table[90] = [393264, 393328, 393712, 394160, 395056, 400944, 407600, 421936, 450608, 507952, 458800, 393264]
ascii_table[92] = [393216, 507904, 260096, 16128, 2032, 248, 24]
ascii_table[95] = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
ascii_table[97] = [480, 13296, 26160, 26160, 26160, 26160, 30304, 16368, 8176]
ascii_table[98] = [524272, 524272, 12384, 24624, 24624, 24624, 24624, 28784, 16352, 3968]
ascii_table[99] = [3968, 16352, 14560, 28784, 24624, 24624, 24624, 24624, 12384]
ascii_table[100] = [3968, 16352, 28784, 24624, 24624, 24624, 24624, 12384, 524272, 524272]
ascii_table[101] = [3968, 16320, 13920, 26224, 26160, 26160, 26160, 30256, 15920, 7776]
ascii_table[102] = [24576, 24576, 262128, 524272, 417792, 417792, 417792]
ascii_table[103] = [3968, 16358, 28787, 24627, 24627, 24627, 24627, 12390, 32766, 32760]
ascii_table[104] = [524272, 524272, 12288, 24576, 24576, 24576, 28672, 16368, 8176]
ascii_table[105] = [425968, 425968]
ascii_table[106] = [3, 3, 425983, 425980]
ascii_table[107] = [524272, 524272, 1792, 3968, 7616, 14560, 28784, 24624, 16400]
ascii_table[108] = [524272, 524272]
ascii_table[109] = [32752, 32752, 12288, 24576, 24576, 24576, 28672, 16368, 8176, 12288, 24576, 24576, 24576, 28672, 16368, 8176]
ascii_table[110] = [32752, 32752, 12288, 24576, 24576, 24576, 28672, 16368, 8176]
ascii_table[111] = [3968, 16352, 12384, 24624, 24624, 24624, 24624, 12384, 16352, 3968]
ascii_table[112] = [32767, 32767, 12384, 24624, 24624, 24624, 24624, 28784, 16352, 3968]
ascii_table[113] = [3968, 16352, 28784, 24624, 24624, 24624, 24624, 12384, 32767, 32767]
ascii_table[114] = [32752, 32752, 12288, 24576, 24576, 24576]
ascii_table[115] = [15456, 15408, 26160, 26160, 26160, 26416, 25568, 12768]
ascii_table[116] = [24576, 262112, 262128, 24624, 24624, 24624, 24624]
ascii_table[117] = [32704, 32736, 112, 48, 48, 48, 96, 32752, 32752]
ascii_table[118] = [16384, 30720, 15872, 1984, 496, 48, 496, 1984, 15872, 30720, 16384]
ascii_table[119] = [24576, 32256, 8128, 496, 240, 4032, 32256, 24576, 32256, 4032, 240, 496, 8128, 32256, 24576]
ascii_table[120] = [16400, 24624, 28784, 14816, 8064, 1792, 8064, 14816, 28784, 24624, 16400]
ascii_table[121] = [16384, 30723, 15875, 3975, 1022, 124, 992, 3968, 15872, 28672, 16384]
ascii_table[122] = [24624, 24688, 25072, 25584, 26416, 28208, 31792, 28720, 24624]
ascii_table[126] = [1536, 1536, 3072, 3072, 3072, 3072, 3584, 1536, 1536, 1536, 1536, 1024, 3072]

num_table = [[0]] * 128
# The 10 px tall numbers for the header font size.
num_table[0] = [254, 511, 1023, 769, 512, 512, 512, 769, 1023, 511, 254]
num_table[1] = [768, 768, 512, 1023, 1023, 1023]
num_table[2] = [896, 769, 515, 519, 519, 527, 798, 1020, 1016, 496]
num_table[3] = [769, 512, 560, 560, 560, 560, 889, 1023, 991, 463]
num_table[4] = [14, 62, 118, 486, 902, 774, 1023, 1023, 1023, 6, 6]
num_table[5] = [1, 1008, 992, 992, 608, 608, 625, 639, 575, 31]
num_table[6] = [126, 511, 1023, 881, 608, 608, 625, 639, 831, 31]
num_table[7] = [512, 512, 512, 515, 527, 639, 1020, 1008, 960, 768]
num_table[8] = [463, 1023, 1023, 569, 560, 560, 569, 1023, 1023, 463]
num_table[9] = [496, 1017, 1020, 796, 524, 524, 797, 1023, 1023, 252]
# The 12 px tall numbers for cryo temps and lhc3.png
num_table[10] = [504, 2046, 3591, 3075, 3075, 3075, 3591, 2046, 504]
num_table[11] = [1539, 3587, 3075, 4095, 4095, 3, 3, 3]
num_table[12] = [1539, 3079, 3087, 3103, 3131, 3699, 2019, 963]
num_table[13] = [1542, 3075, 3267, 3267, 3267, 3267, 3303, 2046, 1852]
num_table[14] = [28, 124, 492, 972, 3852, 3084, 4095, 4095, 12, 12]
num_table[15] = [4070, 4035, 3267, 3267, 3267, 3267, 3303, 3198, 60]
num_table[16] = [504, 2046, 1767, 3267, 3267, 3267, 3303, 1662, 60]
num_table[17] = [3072, 3072, 3073, 3079, 3103, 3192, 4064, 3968, 3584]
num_table[18] = [1852, 4094, 3303, 3267, 3267, 3267, 3303, 4094, 1852]
num_table[19] = [960, 2022, 3699, 3123, 3123, 3123, 3702, 2046, 504]
# The 11 px tall numbers for cryo header time
num_table[20] = [508, 1022, 1539, 1025, 1025, 1539, 1022, 508]
num_table[21] = [512, 1537, 1025, 2047, 2047, 1, 1]
num_table[22] = [513, 1027, 1031, 1037, 1049, 1649, 993, 449]
num_table[23] = [514, 1025, 1057, 1057, 1057, 1651, 1022, 990]
num_table[24] = [56, 104, 136, 776, 1544, 1032, 2047, 2047, 8, 8]
num_table[25] = [2018, 1985, 1089, 1089, 1089, 1123, 1086, 28]
num_table[26] = [252, 1022, 1635, 1089, 1089, 1123, 574, 28]
num_table[27] = [1024, 1024, 1027, 1039, 1086, 1520, 1984, 1792]
num_table[28] = [990, 2015, 1651, 1057, 1057, 1651, 2015, 990]
num_table[29] = [448, 994, 1585, 1041, 1041, 1587, 1022, 504]
# 11 px ':', 12 px '-', '.', 'N', 'S', 'a' and 'm'
num_table[30] = [231, 231]
num_table[31] = [48, 48, 48, 48, 48]
num_table[46] = [7, 7]
num_table[78] = [4095, 4095, 3840, 1920, 480, 120, 30, 15, 4095, 4095]
num_table[83] = [902, 1987, 3267, 3299, 3171, 3187, 3123, 3646, 28]
num_table[97] = [30, 191, 435, 435, 435, 438, 511, 255]
num_table[109] = [511, 511, 192, 384, 384, 384, 511, 255, 192, 384, 384, 384, 511, 255]
# These are 10 px '-', ':', 'G' and 'Z' (Z for ion physics)
num_table[45] = [28, 28, 28, 28, 28, 28]
num_table[58] = [225, 225, 225]
num_table[71] = [124, 511, 1023, 899, 769, 512, 512, 512, 536, 536, 543, 799, 31]
num_table[90] = [513, 515, 519, 527, 574, 636, 760, 992, 960, 896, 768]


def slicetoint(img_slice: list[int]) -> int:
    """slice is a list of integers, which are either 0 or 255.
    Change 255 to 1 to get a binary number, return it as int.
    """
    binary = '0b'
    for i in img_slice:
        if i == 0:
            binary += '0'
        else:
            binary += '1'
    return int(binary, 2)


def decode(glyph: list[int]) -> str:
    """Find the matching character to a list of ints.
    It can return a string containing multiple characters.
    """
    if len(glyph) > 40:
        return '<...>'
    try:
        c = ascii_table.index(glyph)
    except ValueError:
        # glyph may contain stylistic ligatures.
        # Separate and recognise these using recursion.
        # Max depth found so far is 3, for "rve" and "EXT"
        for i in range(4, len(glyph)):
            if glyph[0:i] in ascii_table:
                ligature = chr(ascii_table.index(glyph[0:i]))
                ligature += decode(glyph[i:])
                return ligature
        return '…'
    else:
        return chr(c)


def decode_num(glyph: list[int]) -> str:
    """Find the matching character from the alternative list.
    Returns one character only.
    """
    try:
        char_index = num_table.index(glyph)
    except ValueError:
        # Cryo time '4' gets glued to others in ligatures
        if glyph[:10] == num_table[24]:
            return f"4{decode_num(glyph[10:])}"
        # Cryo time '4' loses one pixel when it's the last digit
        if glyph + [8] == num_table[24]:
            return "4"
        return '…'
    else:
        if char_index < 10:
            c = str(char_index)
        elif char_index >= 10 and char_index < 20:
            c = str(char_index-10)
        elif char_index >= 20 and char_index < 30:
            c = str(char_index-20)
        elif char_index == 30:
            c = ':'
        elif char_index == 31:
            c = '-'
        elif char_index >= 33:
            c = chr(char_index)
        return c


def l_or_i(text: str) -> str:
    """I and l look identical. Try to discern them by context."""
    l = 0
    for i in range(0, text.count('l')):
        its_i = False
        l = text.index('l', l)
        if l == len(text) - 1:
            if text[l-1].isupper():
                text = text[:l] + 'I'
            break
        elif l == 0 or not text[l-1].isalpha():
            if text[l+1].isupper() or text[l+1] in ('n', 'p', 's'):
                its_i = True
        elif text[l-1].isupper() and (not text[l+1].isalpha() or text[l+1].isupper()):
            its_i = True
        if its_i:
            text = text[:l] + 'I' + text[l+1:]
            its_i = False
        else:
            l += 1
    text = text.replace(' lon ', ' Ion ')
    text = text.replace(' lons', ' Ions')
    text = text.replace('\nlon ', '\nIon ')
    text = text.replace('\nlons', '\nIons')
    text = text.replace(' ll\n', ' II\n')
    text = text.replace('EIQA', 'ElQA')
    text = text.replace('Flll', 'FIll')
    text = text.replace('flll', 'fIll')
    text = text.replace('MKl', 'MKI')
    text = text.replace('TDl', 'TDI')
    text = text.replace('alllPs', 'allIPs')
    return text


def tess(img: Image.Image) -> str:
    """Use tesserocr to get text when built-in ocr fails."""
    img = img.convert(mode='RGB')
    img = ImageOps.invert(img)
    img = img.resize((int(img.width*1.6), int(img.height*1.6)), resample=Image.Resampling.BICUBIC)
    text = ''
#    with PyTessBaseAPI(path='/usr/share/tessdata/.', lang='eng', oem=OEM.LSTM_ONLY, psm=PSM.SINGLE_BLOCK) as tesseract:
#        tesseract.SetImage(img)
#        text = tesseract.GetUTF8Text()
    text = text.replace('—', '-')
    first = True
    for t in text.splitlines():
        if first:
            text = t
            first = False
        elif t:
            text += '\n' + t
    logging.warning('Tesseract fallback')
    return text


def ocr(image: Image.Image, identify: bool = False) -> str:
    """Take the image and crop it to a single line if necessary. Read
    the line one slice at a time, identifying individual characters
    by the black slice that follows it, then decode that character.
    Spaces are detected by counting consecutive black slices.
    The identify bool enables returning a tuple for unknown characters.
    """
    text = ''
    parsing_number = False
    max_lines = 7
    first_line = 23
    line_height = 20
    next_line = 24
    # Comments are taller than 16px, the rest use the other table.
    if image.height <= 16:
        max_lines = 1
        first_line = image.height
        line_height = image.height
        parsing_number = True
    # Machine mode and fill scheme from lhcconfig are the same font
    # as comments, 17px tall for I/l differentiation.
    elif image.height == 20:
        max_lines = 1
        first_line = image.height
        line_height = 20
        parsing_number = False
    line_bottom = first_line
    for j in range(max_lines):
        line_top = line_bottom - line_height
        line = image.crop((0, line_top, image.width, line_bottom))
        bbox = line.getbbox()
        if bbox is not None and bbox[2] < image.width:
            if len(text):
                text += '\n'
            line = line.crop((bbox[0], 0, bbox[2]+1, line_height))
            width = line.width
            linelist = list(line.getdata(0))
            glyph = []
            blanks = 0
            blank_slice = [0] * line_height
            for i in range(width):
                img_slice = linelist[i::width]
                if img_slice != blank_slice:
                    glyph.append(slicetoint(img_slice))
                else:
                    if glyph != []:
                        if parsing_number:
                            c = decode_num(glyph)
                            # For energy, return at the first letter
                            if c in ('G', 'Z'):
                                return text
                        else:
                            c = decode(glyph)
                        # Remove the detected space before '/' and '>'
                        if c in ('/', '>'):
                            if text[-1] == ' ' and blanks == 5:
                                text = text[:-1]
                        elif c == '…' and max_lines > 1:
                            if identify:
                                # glyph_pos = bbox[0] + i
                                return ''
                                # return (glyph, (glyph_pos-len(glyph)-1,
                                #                 line_top-3, glyph_pos+1,
                                #                 line_bottom+3))
                            else:
                                end_of_first_line = text.find(')')
                                if not end_of_first_line:
                                    skip = 0
                                    text = ''
                                else:
                                    skip = 24
                                    text = text[:end_of_first_line+2]
                                text += tess(image.crop((0, skip,
                                                         image.width,
                                                         image.height-1)))
                                return text
                        text += c
                        glyph = []
                        blanks = 0
                    else:
                        blanks += 1
                    if blanks == 5 and not parsing_number:
                        text += ' '
                    elif blanks == 8 and parsing_number:
                        text += ' '
                    elif blanks > 11:
                        text += ' '
                        blanks = 0
        if j == 0:
            line_bottom += 3
        line_bottom += next_line
    if 'l' in text and image.height >= 20:
        text = l_or_i(text)
    text = text.replace('\'\'', '\"')
    return text
