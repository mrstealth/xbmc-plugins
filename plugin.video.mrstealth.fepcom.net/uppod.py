#-------------------------------------------------------------------------------
# Uppod decoder
#-------------------------------------------------------------------------------

import urllib2

def decode(param):
        try:
            #-- define variables
            loc_3 = [0,0,0,0]
            loc_4 = [0,0,0]
            loc_2 = ''

            #-- define hash parameters for decoding
            dec = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/='
            hash1 = ["0", "5", "u", "w", "6", "n", "H", "o", "B", "p", "N", "M", "D", "R", "z", "G", "V", "e", "i", "3", "m", "W", "U", "7", "g", "="]
            hash2 = ["c", "T", "I", "4", "Q", "Z", "v", "Y", "y", "X", "k", "b", "8", "a", "J", "d", "1", "x", "L", "t", "l", "2", "f", "s", "9", "h"]
            #-- decode
            for i in range(0, len(hash1)):
                re1 = hash1[i]
                re2 = hash2[i]

                param = param.replace(re1, '___')
                param = param.replace(re2, re1)
                param = param.replace('___', re2)

            i = 0
            while i < len(param):
                j = 0
                while j < 4 and i+j < len(param):
                    loc_3[j] = dec.find(param[i+j])
                    j = j + 1

                loc_4[0] = (loc_3[0] << 2) + ((loc_3[1] & 48) >> 4);
                loc_4[1] = ((loc_3[1] & 15) << 4) + ((loc_3[2] & 60) >> 2);
                loc_4[2] = ((loc_3[2] & 3) << 6) + loc_3[3];

                j = 0
                while j < 3:
                    if loc_3[j + 1] == 64 or loc_4[j] == 0:
                        break

                    loc_2 += unichr(loc_4[j])

                    j = j + 1
                i = i + 4;
        except:
            loc_2 = ''

        return loc_2


def decodeSourceURL(uhash):
    print "*** [uppod.py-decodeSourceURL] Got uppod uhash \n%s" % uhash
    return decode(uhash)

def getDecodedHashFromSourceURL(url, referer):
    print "*** [uppod.py-getDecodedHashFromSourceURL] Decoded source URL \n%s" % url
    request = urllib2.Request(url, None)
    request.add_header('Referer', referer)
    return urllib2.urlopen(request).read()
