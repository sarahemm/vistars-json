from PIL import Image
from ocr import slicetoint, l_or_i

pm_ascii_table = [[0]] * 128
# ff ligature
pm_ascii_table[6] = [6144, 6144, 65528, 65528, 38912, 38912, 38912, 6144, 65528, 65528, 38912, 38912, 38912]
pm_ascii_table[33] = [65432, 65432]
pm_ascii_table[35] = [384, 6528, 6584, 7152, 32640, 63872, 6648, 8160, 32128, 55680, 6528, 6144]
pm_ascii_table[37] = [31744, 65024, 33280, 33288, 65072, 31840, 384, 512, 3072, 12784, 25592, 33288, 520, 1016, 496]
pm_ascii_table[38] = [480, 1008, 15928, 31768, 52760, 50968, 50072, 49648, 24816, 952, 792, 8]
pm_ascii_table[39] = [63488, 63488]
pm_ascii_table[40] = [4032, 32760, 57374, 2]
pm_ascii_table[41] = [2, 57374, 32760, 4032]
pm_ascii_table[42] = [16896, 9216, 6144, 65280, 6144, 9216, 16896]
pm_ascii_table[44] = [2, 28, 24]
pm_ascii_table[45] = [384, 384, 384, 384, 384]
pm_ascii_table[46] = [24, 24]
pm_ascii_table[47] = [6, 126, 2040, 16320, 64512, 49152]
pm_ascii_table[48] = [8128, 32752, 57400, 49176, 49176, 49176, 57400, 32752, 8128]
pm_ascii_table[49] = [24600, 24600, 49176, 65528, 65528, 24, 24, 24]
pm_ascii_table[50] = [24600, 49208, 49272, 49368, 49560, 59160, 32280, 15384]
pm_ascii_table[51] = [24624, 49176, 50712, 50712, 50712, 50712, 61240, 32752, 14816]
pm_ascii_table[52] = [192, 960, 1728, 6336, 12480, 49344, 65528, 65528, 192, 192]
pm_ascii_table[53] = [48, 65048, 64536, 52248, 52248, 52792, 51184, 992]
pm_ascii_table[54] = [8128, 16368, 29496, 58904, 50712, 50712, 51000, 25584, 480]
pm_ascii_table[55] = [49152, 49152, 49176, 49400, 51184, 65408, 64512, 49152]
pm_ascii_table[56] = [14816, 32752, 61240, 50712, 50712, 50712, 61240, 32752, 14816]
pm_ascii_table[57] = [15360, 32304, 59160, 49944, 49944, 49976, 58992, 32736, 8128]
pm_ascii_table[58] = [3096, 3096]
pm_ascii_table[59] = [2, 3100, 3096]
pm_ascii_table[61] = [3264, 3264, 3264, 3264, 3264, 3264, 3264, 3264, 3264, 3264, 3264]
pm_ascii_table[62] = [6168, 3120, 3120, 3120, 1632, 1632, 960, 960, 960, 384, 384]
pm_ascii_table[64] = [2016, 8184, 15420, 28686, 24582, 58307, 51171, 50787, 49731, 51171, 51170, 24678, 24640, 12480, 8064, 3840]
pm_ascii_table[65] = [8, 120, 496, 4032, 16064, 61632, 61632, 16064, 4032, 496, 120, 8]
pm_ascii_table[66] = [65528, 65528, 50712, 50712, 50712, 50712, 65336, 31216, 224]
pm_ascii_table[67] = [3968, 16352, 28784, 24624, 49176, 49176, 49176, 49176, 49176, 49176, 24624]
pm_ascii_table[68] = [65528, 65528, 49176, 49176, 49176, 49176, 49176, 24624, 28784, 16352, 8128]
pm_ascii_table[69] = [65528, 65528, 50712, 50712, 50712, 50712, 50712, 50712]
pm_ascii_table[70] = [65528, 65528, 50688, 50688, 50688, 50688, 50688, 49152]
pm_ascii_table[71] = [3968, 16352, 28784, 24632, 49176, 49176, 50712, 50712, 50712, 51184, 26592]
pm_ascii_table[72] = [65528, 65528, 1536, 1536, 1536, 1536, 1536, 1536, 65528, 65528]
# I is identical to l
pm_ascii_table[74] = [1, 1, 3, 65535, 65534]
pm_ascii_table[75] = [65528, 65528, 1536, 3840, 6528, 12480, 24672, 49200, 32792, 8]
pm_ascii_table[76] = [65528, 65528, 24, 24, 24, 24, 24, 24]
pm_ascii_table[77] = [65528, 65528, 57344, 31744, 7936, 960, 960, 3840, 31744, 57344, 65528, 65528]
pm_ascii_table[78] = [65528, 65528, 61440, 15360, 3584, 896, 480, 120, 65528, 65528]
pm_ascii_table[79] = [3968, 16352, 28784, 57400, 49176, 49176, 49176, 49176, 57400, 28784, 16352, 3968]
pm_ascii_table[80] = [65528, 65528, 49920, 49920, 49920, 59136, 32256, 15360]
pm_ascii_table[81] = [3968, 16352, 28784, 57400, 49176, 49176, 49176, 49180, 57406, 28786, 16352, 3968]
pm_ascii_table[82] = [65528, 65528, 49920, 49920, 49920, 59264, 32480, 15480, 24, 8]
pm_ascii_table[83] = [14384, 31768, 58904, 50712, 50712, 50712, 49976, 25584, 480]
pm_ascii_table[84] = [49152, 49152, 49152, 49152, 49152, 65528, 65528, 49152, 49152, 49152, 49152, 49152]
pm_ascii_table[85] = [65472, 65520, 56, 24, 24, 24, 24, 56, 65520, 65472]
pm_ascii_table[86] = [32768, 61440, 31744, 3968, 992, 120, 120, 992, 3968, 31744, 61440, 32768]
pm_ascii_table[87] = [49152, 64512, 16320, 1016, 56, 1016, 16320, 64512, 49152, 64512, 16320, 1016, 56, 1016, 16320, 64512, 49152]
pm_ascii_table[88] = [8, 32792, 57464, 61664, 16320, 3840, 8064, 14816, 61560, 49208, 32776]
pm_ascii_table[89] = [32768, 49152, 57344, 14336, 7168, 2040, 2040, 7168, 14336, 57344, 49152, 32768]
pm_ascii_table[90] = [49176, 49208, 49272, 49656, 50072, 50968, 56856, 64536, 61464, 57368, 49176]
pm_ascii_table[95] = [1, 1, 1, 1, 1, 1, 1, 1, 1]
pm_ascii_table[97] = [240, 3320, 6552, 6552, 6552, 7600, 4088, 2040]
pm_ascii_table[98] = [65528, 65528, 3120, 6168, 6168, 6168, 7224, 4080, 2016]
pm_ascii_table[99] = [960, 4080, 3120, 6168, 6168, 6168, 6168, 3120]
pm_ascii_table[100] = [2016, 4080, 7224, 6168, 6168, 6168, 3120, 65528, 65528]
pm_ascii_table[101] = [960, 4080, 3504, 6552, 6552, 6552, 6552, 7576, 3992, 1968]
pm_ascii_table[102] = [6144, 6144, 65528, 65528, 38912, 38912, 38912]
pm_ascii_table[103] = [2016, 4083, 7225, 6169, 6169, 6169, 3123, 8191, 8188]
pm_ascii_table[104] = [65528, 65528, 3072, 6144, 6144, 7168, 8184, 2040]
pm_ascii_table[105] = [40952, 40952]
pm_ascii_table[106] = [1, 1, 40959, 40959]
pm_ascii_table[107] = [65528, 65528, 384, 960, 1632, 3120, 6168, 4104]
pm_ascii_table[108] = [65528, 65528]
pm_ascii_table[109] = [8184, 8184, 3072, 6144, 6144, 6144, 8184, 2040, 3072, 6144, 6144, 6144, 8184, 2040]
pm_ascii_table[110] = [8184, 8184, 3072, 6144, 6144, 7168, 8184, 2040]
pm_ascii_table[111] = [960, 4080, 3120, 6168, 6168, 6168, 6168, 3120, 4080, 960]
pm_ascii_table[112] = [8191, 8191, 3120, 6168, 6168, 6168, 7224, 4080, 2016]
pm_ascii_table[113] = [2016, 4080, 7224, 6168, 6168, 6168, 3120, 8191, 8191]
pm_ascii_table[114] = [8184, 8184, 3072, 6144, 6144, 6144]
pm_ascii_table[115] = [3632, 7960, 6936, 6552, 6552, 6648, 3312]
pm_ascii_table[116] = [6144, 65520, 65528, 6168, 6168, 6168]
pm_ascii_table[117] = [8160, 8184, 56, 24, 24, 48, 8184, 8184]
pm_ascii_table[118] = [6144, 7680, 1984, 496, 56, 56, 496, 1984, 7680, 6144]
pm_ascii_table[119] = [7168, 8128, 1016, 56, 1016, 8064, 6144, 8064, 1016, 56, 1016, 8128, 7168]
pm_ascii_table[120] = [4104, 6168, 7800, 2016, 384, 384, 2016, 7800, 6168, 4104]
pm_ascii_table[121] = [6144, 7681, 1921, 483, 127, 124, 480, 1920, 7680, 6144]
pm_ascii_table[122] = [6168, 6200, 6392, 6648, 7064, 7960, 7192, 6168]
pm_ascii_table[126] = [768, 1536, 1536, 1536, 1536, 1792, 768, 768, 768, 768, 1536]

def decode(glyph: list[int]) -> str:
    """Find the matching character to a list of ints.
    It can return a string containing multiple characters.
    """
    try:
        return chr(pm_ascii_table.index(glyph))
    except ValueError:
        # glyph may contain ligatures
        # Separate and recognise these using recursion.
        # Max depth found so far is 3, for "rve" and "EXT"
        # Backwards search so "of" is not seen as "c…"
        # The ff ligature needs to be parsed as a whole.
        lg = len(glyph)
        for i in range(lg-3, 3, -1):
            if glyph[i:lg] in pm_ascii_table:
                c = pm_ascii_table.index(glyph[i:lg])
                if c == 6:
                    return decode(glyph[0:i]) + 'ff'
                return decode(glyph[0:i]) + chr(c)
        return '…'


def ocr_pm(image: Image.Image) -> str:
    """Take the image and crop it to a single line if necessary. Read
    the line one slice at a time, identifying individual characters
    by the black slice that follows it, then decode that character.
    Spaces are detected by counting consecutive black slices.
    """
    text = ''
    max_lines = 5
    pm_comment_box = (0, 100, image.width, image.height)
    if image.crop(pm_comment_box).getbbox() is None:
        max_lines -= 1
    first_line = 21
    line_height = 16
    next_line = 24
    line_bottom = first_line
    for j in range(max_lines):
        line_top = line_bottom - line_height
        line = image.crop((0, line_top, image.width, line_bottom))
        bbox = line.getbbox()
        if bbox is not None:
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
                        c = decode(glyph)
                        text += c
                        glyph = []
                        blanks = 0
                    else:
                        blanks += 1
                    if blanks == 4:
                        text += ' '
                    elif blanks > 11 and text[-2:] != ': ':
                        text += ' '
                        blanks = 0
        line_bottom += next_line
    if 'l' in text:
        text = l_or_i(text)
    text = text.replace('\'\'', '\"')
    return text
