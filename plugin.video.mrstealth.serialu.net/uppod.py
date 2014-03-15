#-------------------------------------------------------------------------------
# Uppod decoder
#-------------------------------------------------------------------------------

import urllib2
import cookielib

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
    print "*** Got uppod uhash: %s" % uhash
    return decode(uhash)

def getDecodedHashFromSourceURL(url, referer):
    print "*** Decoded source URL: %s" % url

    # NOTE: set cookie
    cj = cookielib.MozillaCookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    urllib2.install_opener(opener)

    # Accept  text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
    # Accept-Encoding gzip, deflate
    # Accept-Language de-de,de;q=0.8,en-us;q=0.5,en;q=0.3
    # Connection  keep-alive
    # Cookie  SERIALU=cd640e59142f39cc54ed65461dd60e10; MarketGidStorage=%7B%220%22%3A%7B%22svspr%22%3A%22%22%2C%22svsds%22%3A3%2C%22TejndEEDj%22%3A%22MTM4MDU1NzM0NTY2NTQ0OTk0NTMz%22%7D%2C%22C44994%22%3A%7B%22page%22%3A3%2C%22time%22%3A1380557356398%7D%7D; amcu_n=2; advmaker_pop=1
    # DNT 1
    # Host    serialu.net
    # Referer http://serialu.net/media/stil-nov/uppod.swf
    # User-Agent  Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:24.0) Gecko/20100101 Firefox/24.0

    request = urllib2.Request(url, None)
    request.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
    request.add_header('Accept-Encoding', 'gzip, deflate')
    request.add_header('Accept-Language', 'de-de,de;q=0.8,en-us;q=0.5,en;q=0.3')
    request.add_header('Connection', 'keep-alive')
    # request.add_header('Cookie', 'SERIALU=cd640e59142f39cc54ed65461dd60e10; MarketGidStorage=%7B%220%22%3A%7B%22svspr%22%3A%22%22%2C%22svsds%22%3A3%2C%22TejndEEDj%22%3A%22MTM4MDU1NzM0NTY2NTQ0OTk0NTMz%22%7D%2C%22C44994%22%3A%7B%22page%22%3A3%2C%22time%22%3A1380557356398%7D%7D; amcu_n=2; advmaker_pop=1')
    request.add_header('DNT', 1)
    request.add_header('Host', 'serialu.net')
    request.add_header('Referer', 'http://serialu.net/media/stil-nov/uppod.swf')
    request.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:24.0) Gecko/20100101 Firefox/24.0')

    return urllib2.urlopen(request).read()
