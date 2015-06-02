""" A messy scraper for a messy website (with messy addresses) """

import requests
import json
import sys
import time
from bs4 import BeautifulSoup

SITE_URL = 'http://www.shift2bikes.org/cal/viewpp2015.php'
OUT_FILE = 'schedule.json'
IN_FILE = 'copy.php'

NOMINATIM_URL = 'http://nominatim.openstreetmap.org/search?q='

S_DIG_DATES = [('div2015-06-0' + str(x)) for x in range(4, 10)]
D_DIG_DATES = [('div2015-06-' + str(x)) for x in range(10, 28)]
DATE_LIST = S_DIG_DATES + D_DIG_DATES

#r = requests.get(SITE_URL)
#print r.text
#soup = BeautifulSoup(r.text)

with open(IN_FILE, 'r') as inp:
    soup = BeautifulSoup(inp)
#print soup.prettify()

def cap(s, l):
    return s if len(s)<=l else s[0:l-3]+'...'

def clean(string):
    return string.replace('\r', '')

def geocode(address):
    r2 = requests.get(NOMINATIM_URL + address + '&format=json&limit=1&bounded=1&viewbox=-123.3%2C45.2%2C-122.0%2C46.0')
    l = r2.json()
    if l:
        return l[0]
    else:
        return None

data = {}
count = 0
geo_fail_count = 0
for child in soup.body.find_all('div'):
    if 'id' in child.attrs:
        if child['id'] in DATE_LIST:
            date = child['id'][-2:]
            print '\n--- Date: June ' + date + ' ---'
            data[date] = []
            for listing in child.find_all('dt'):
                event = {}
                event['id'] = listing.a.attrs['name']
                event['link'] = SITE_URL + '#' + event['id']
                event['name'] = listing.a.contents[0].strip()#.title()
                details = listing.next_sibling

                # first way to get loc
                loc = details.contents[0].contents[0].string.strip()
                if details.contents[0].contents[-1].string:
                    loc = loc + ' ' + details.contents[0].contents[-1].string.strip()
                if ', ' in details.contents[0].contents[0].string:
                    split_loc = details.contents[0].contents[0].string.split(', ')
                    addr = ', '.join(split_loc[1:]).strip()
                else:
                    addr = details.contents[0].contents[0].string.strip()

                # second way to get loc
                if loc == '':
                    loc = details.contents[0].contents[1].contents[0].string.strip()
                    if details.contents[0].contents[1].contents[-1].string:
                        loc = loc + ' ' + details.contents[0].contents[1].contents[-1].string.strip()
                    if ', ' in details.contents[0].contents[1].contents[0].string:
                        split_loc = details.contents[0].contents[1].contents[0].string.split(', ')
                        addr = ', '.join(split_loc[1:]).strip()
                    else:
                        addr = details.contents[0].contents[1].contents[0].string.strip()
                
                # geocoding overrides -- TODO: make not ridiculously terrible
                if addr == 'TBD' or 'TBA' in loc or 'Somewhere in the SE, maybe NE?' in loc:
                    addr = 'TBA'
                if 'SW Knight and Fairview' in loc:
                    addr = 'Washington Park MAX'
                if 'Burnside, and Hawthorne bridges, Steel, Burnside, and Hawthorne bridges' in loc or 'Burnside, and Hawthorne bridges, bridgey' in loc:
                    addr = '400 Northeast Couch Street, Portland'
                if 'Coe Circle' in loc:
                    addr = 'Coe Circle, Portland'
                if 'Clinton City Park' in loc:
                    addr = 'Clinton Park, Portland'
                if 'Salmon Street Springs Fountain' in loc or 'Salmon Street Fountain' in loc or 'Salmon St. Springs' in loc or 'SW Naito Pkwy and Main St' in loc or 'Salmon Street Springs' in loc:
                    addr = 'Salmon Street Springs Fountain'
                if 'Pioneer Courthouse Square' in loc:
                    addr = 'Pioneer Courthouse Square, Portland'
                if 'Washington High School' in loc:
                    addr = 'Washington High School, Portland'
                if 'Unthank Park' in loc:
                    addr = 'Unthank Park, Portland'
                if '1810 NE First Avenue' in loc or 'Bikefarm' in loc:
                    addr = '1810 NE 1st Avenue, Portland'
                if 'Vera Katz Statue' in loc or 'Vera Katz statue' in loc:
                    addr = 'Vera Katz Statue, Portland'
                if 'Union Station' in loc:
                    addr = 'Portland Union Station'
                if 'Laurelhurst Park' in loc or 'Laurelhurst City Park' in loc:
                    addr = 'Laurelhurst Park'
                if 'Col. Summers Park' in loc or 'Colonel Sumner Park' in loc:
                    addr = 'Colonel Summers Park'
                if 'Zoobomb Pyle' in loc:
                    addr = '400 SW 13th Ave, Portland'
                if 'Kenilworth Park' in loc:
                    addr = 'Kenilworth Park, Portland'
                if 'Portland Building' in loc or 'Portlandia Statue' in loc:
                    addr = 'The Portland Building'
                if 'Peninsula Park' in loc or 'Peninsula City Park' in loc or 'Penninsula Park' in loc or 'Peninsular Park' in loc:
                    addr = 'Peninsula Park, Portland'
                if 'Sewallcrest Park' in loc:
                    addr = 'Sewallcrest Park, Portland'
                if 'Irving Park' in loc:
                    addr = 'Irving Park, Portland'
                if 'Stub Stewart State Park' in loc:
                    addr = 'LL Stub Stewart Memorial State Park, 97109'
                if 'Brickhouse, 109 W 15th St' in loc:
                    addr = '1450 Main Street, Vancouver'
                if 'Ladd Circle' in loc or 'Ladd\'s Circle' in loc:
                    addr = 'Ladd Circle, Portland'
                if 'Peoples Coop' in loc:
                    addr = 'People\'s Food Co-op'
                if 'SE 15th & Alder St' in loc:
                    addr = '700 Southeast 15th Avenue, Portland'
                if 'SE 16th and Brooklyn' in loc:
                    addr = '1600 Southeast Brooklyn Street, Portland'
                if 'Riverdale High School' in loc:
                    addr = 'Riverdale High School, Portland'
                if 'Portland Autonomous Zone' in loc or 'PAZ' in loc:
                    addr = '1624 SE Woodward St Portland, OR 97202'
                if 'SE 9th Ave. & Ankeny' in loc:
                    addr = '901 Southeast Ankeny, Portland'
                if 'Dawson Park' in loc:
                    addr = 'Dawson Park, Portland'
                if 'O\'Bryant Square' in loc:
                    addr = 'O\'Bryant Square, Portland'
                if 'N Williams & NE Tillamook' in loc:
                    addr = '2124 N Williams Ave, Portland'
                if '2020 SE Bush Street' in loc:
                    addr = '3784 SE 21st Ave, Portland'
                if 'Purrington\'s' in loc:
                    addr = '3529 MLK, Portland, OR, 97212'
                if 'Devil\'s Point' in loc:
                    addr = 'Devil\'s Point, Portland'
                if 'Apex' in loc:
                    addr = 'Apex, Central East Side, Portland'
                if 'NE 11th and Alberta' in loc:
                    addr = '1100 NE Alberta St, Portland'
                if 'SE 42nd Ave and SE Morrison St' in loc:
                    addr = '4200 SE Morrison St, Portland'
                if 'SE 16th Ave and SE Ash St' in loc:
                    addr = '1600 SE Ash St, Portland'
                if 'SE 9th Ave and SE Sherrett St' in loc:
                    addr = '900 SE Sherrett St, Portland'
                if 'Marine Drive Bike Path at NE 33rd Ave' in loc:
                    addr = 'Northeast 33rd Drive, Faloma, Portland, 97211'
                if 'Hatfield Government Center MAX stop' in loc or 'Hatfield Government Center MAX Station' in loc:
                    addr = 'Hatfield Government Center, Hillsboro'
                if '4250 NW Leif Erikson Dr, Portland' in loc or 'Forest Park, top of NW Thurman St' in loc:
                    addr = 'drinking water, Northwest Leif Erikson Drive'
                if 'Fields Park' in loc:
                    addr = 'Fields Park, Portland'
                if 'NE Weidler St & NE 28th Ave' in loc:
                    addr = '2801 NE Weidler St, Portland'
                if 'Cartlandia' in loc:
                    addr = 'Cartlandia, Portland'
                if 'NE 7th & Morris' in loc:
                    addr = '699 NE Morris St, Portland'
                if 'Hopworks Bike Bar' in loc:
                    addr = '3947 North Williams Ave, Portland'
                if 'Southeast Grind' in loc:
                    addr = 'Southeast Grind, Portland'
                if 'Everybody\'s Bike Rentals' in loc:
                    addr = 'Everybody\'s Bike Rentals, Portland'
                if 'Circa Cycles' in loc:
                    addr = '1720 NW Lovejoy St, Portland'
                if 'SE Marine Park Way and Columbia Way' in loc:
                    addr = 'Marine Park, Vancouver'
                if 'N Saint Louis Ave & N Edison St' in loc:
                    addr = '9080 N Edison St, Portland'
                if 'Kenton Park' in loc:
                    addr = 'Kenton Park, Portland'
                if 'Jamison Square' in loc:
                    addr = 'Jamison Square, Portland'
                if 'Exiled Records' in loc:
                    addr = 'Exiled Records, Portland'
                if 'Peninsula Park' in loc:
                    addr = 'Peninsula Park, Portland'
                if 'Base Camp Brewing' in loc:
                    addr = 'Base Camp Brewing, Portland'
                if 'Clever Cycles' in loc:
                    addr = 'Clever Cycles, Portland'
                if 'Marquam Beach' in loc:
                    addr = 'slipway, south waterfront park, Portland'
                if 'Khunamokwst Park' in loc or 'K&#688;unamokwst Park' in loc:
                    addr = 'Werbin Property, Portland'
                if 'Director Park' in loc:
                    addr = 'Director Park, Portland'
                if 'Naito Legacy Fountain' in loc or 'Saturday Market Fountain' in loc:
                    addr = 'Bill Naito Legacy Fountain, Portland'
                if 'Oregon Park' in loc:
                    addr = 'Oregon Park, Portland'
                if '7238 N Burlington Ave' in loc:
                    addr = '7238 N Burlington Ave, Portland'
                if 'Creston outdoor pool' in loc:
                    addr = 'Creston Park, Portland'
                if 'North Bar' in loc or 'SE 50th Ave and Division St' in loc:
                    addr = 'North, Southeast Division Street, Portland'
                if '4500 SE Stark' in loc:
                    addr = '4500 Southeast Stark Street, Portland, 97215'
                if 'NW Flanders & 23rd' in loc:
                    addr = '2300 Northwest Flanders Street, Portland'
                if 'NE Oregon St & NE Lloyd Blvd' in loc:
                    addr = '1 NE Lloyd Blvd, Portland'
                if '4926 Southeast Division Street Portland' in loc:
                    addr = '2404 Southeast 49th Ave, Portland'
                if 'Patton Square City Park' in loc:
                    addr = 'Patton Square Park, Portland'
                if 'Reed College' in loc:
                    addr = 'Reed College, Portland'
                if 'Woodlawn Park' in loc:
                    addr = 'Woodlawn Park, Portland'
                if 'Lone Fir Cemetery' in loc:
                    addr = 'Lone Fir Cemetery, Portland'
                if 'Holladay Park' in loc:
                    addr = 'Holladay Park, Portland'
                if 'Alberta Park' in loc:
                    addr = 'Alberta Park, Portland'
                if 'N Omaha Av at Ainsworth St' in loc:
                    addr = '2300 North Ainsworth Street, Portland'
                if 'Barley Mill Pub' in loc:
                    addr = 'McMenamins Barley Mill Pub, Portland'
                if '2216 NE Martin Luther King Jr Blvd' in loc:
                    addr = '2216 Northeast Martin Luther King Junior Boulevard, Portland'
                if 'Sabin HydroPark' in loc:
                    addr = 'Sabin HydroPark, Portland'
                if 'North Park Blocks' in loc:
                    addr = '34 Northwest 8th Ave, Portland'
                if 'South Park Blocks' in loc:
                    addr = '1200 SW Park Avenue, Portland'
                if 'SE 11th Ave and Division St' in loc:
                    addr = '1100 Southeast Division Street, Portland'
                if 'Proper Eats' in loc:
                    addr = '7399 North Alta Avenue, Portland'
                if 'Skidmore Fountain' in loc:
                    addr = 'Skidmore Fountain, Portland'
                if 'Steel Bridge West End' in loc or 'Beach on West End of Steel Bridge' in loc:
                    addr = '370 Northwest Naito Parkway, Portland'
                if 'NE 8th ave. and Alberta' in loc:
                    addr = '800 Northeast Alberta Street, Portland'
                if 'Beaverton Creek MAX Station' in loc:
                    addr = 'Beaverton Creek MAX Station, Beaverton'
                if 'SE 47th and SE Center St' in loc:
                    addr = '4699 SE Center St, Portland'
                if '5421 N Greely Ave' in loc:
                    addr = '5421 N Greeley Ave, Portland'
                if 'East Bank Esplanade, under Burnside Bridge' in loc:
                    addr = 'Vera Katz Eastbank Esplanade, Lloyd District, Portland'
                if 'Bicycle Transportation Alliance' in loc:
                    addr = '618 NW Glisan St, Portland'
                if 'SW Montgomery Ave and SW Park Ave' in loc:
                    addr = 'South Park Blocks, Southwest 9th Avenue, University District, Portland'
                if 'NE Rodney at Ivy' in loc:
                    addr = '3368 NE Rodney Ave, Portland'
                if 'Normandale Park' in loc:
                    addr = 'Normandale Park, Portland'
                if 'N WIllamette Blvd and N Ida Ave' in loc:
                    addr = '6912 N Ida Ave, Portland'
                if '401 SE Caruthers' in loc:
                    addr = '401 Southeast Caruthers, Portland, 97214'
                if 'River City Bicycles' in loc:
                    addr = 'River City Bicycles, Portland'
                if 'Florida Room' in loc:
                    addr = '475 N Killingsworth St, Portland'
                if 'Water Avenue Coffee' in loc:
                    addr = '1028 SE Water Ave 97214'
                if 'USS Oregon Memorial' in loc:
                    addr = 'USS Oregon Memorial, Portland'
                if '1221 SW 4th Ave' in loc:
                    addr = 'Portland City Hall, University District'
                if '4831 NE 42nd Ave' in loc:
                    addr = '4831 NE 42nd Ave, Portland'
                if 'In Other Words' in loc:
                    addr = 'In Other Words, Portland'
                if 'Portland Button Works' in loc:
                    addr = '1322 N Killingsworth St, Portland'
                if '6340 SE Foster' in loc:
                    addr = '6340, Southeast Foster Road, Foster-Powell, Woodstock, Portland'
                if 'Upper Siouxon Trailhead' in loc:
                    addr = 'Siouxon Trail, Skamania County'

                print '\n' + event['name']
                print loc
                event['location'] = loc
                if addr:
                    event['address'] = addr
                else:
                    event['address'] = ''

                #sort out time & if cancelled
                if details.contents[0].next_sibling:
                    event['time'] = details.contents[0].next_sibling.strip()
                else:
                    event['time'] = ''
                if event['time'] == '':
                    if details.contents[0].contents[1].next_sibling:
                        event['time'] = details.contents[0].contents[1].next_sibling.strip()

                # geocoding!
                if event['time'] != 'CANCELED' and event['address'] != 'TBA' and event['id'] != '14-4950':
                    if event['address'] != '':
                        try:
                            geo = geocode(event['address'].replace(' ', '+'))
                            time.sleep(1)  # so nominatim doesn't get mad
                            if geo:
                                print 'Geocoded to: ' + geo['display_name']
                                lat = float(geo['lat'])
                                lon = float(geo['lon'])
                                if ((lat < 45) or (lon > -121)):
                                    event['coordinates'] = []
                                    print '*** discarded this latlong, out of PDX'
                                else: 
                                    event['coordinates'] = [lon, lat]
                            else:
                                event['coordinates'] = []
                                print '*** geocoding unsuccessful'
                        except:
                            print 'problem contacting geocoding service, stopping'
                            sys.exit(1)
                    else:
                        event['coordinates'] = []
                        print '*** geocoding unsuccessful'

                    details_divs = details.find_all('div')
                    description = ''
                    i_count = 0
                    last_string = ''
                    for c in details_divs[1].em.children:
                        if c.string:
                            description = description + clean(c.string)
                        else:
                            for i in c.descendants:
                                i_count += 1
                                if i.string:
                                    i_str = (i.string.replace('<br>', ' ').replace('</br>', '').replace('\n', ' ')).replace('  ', ' ')
                                    if i_str != last_string:
                                        last_string = i_str
                                        description = description + i_str
                    event['description'] = cap(description.replace('    ', ' ').replace('   ', ' ').replace('  ', ' ').replace(u'\xc2\xc2\xc2', ' ').replace(u'\xa0', ' ').replace(u'\xe2', "'").replace(u'\xc2\xc2', ' ').replace(u'\xc2', ' '), 139)
                    #print 'FINAL DESCRIPTION: ' + event['description']
                    #print 'time: ' + event['time']
                    data[date].append(event)
                    count += 1
                    if event['coordinates'] == []:
                        geo_fail_count += 1
                    #print event
                else:
                    print '*** skipping cancelled/TBA event ' + event['name']

print '\n' + 'Number of non-cancelled/non-TBA events: ' + str(count)
print 'Number of geo-fails: ' + str(geo_fail_count)

with open(OUT_FILE, 'w') as out:
    out.write('var days = ' + json.dumps(data, separators=(',', ': '), indent=2, sort_keys=True))
