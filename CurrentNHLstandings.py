import re
from urllib.request import urlopen
import ssl

n=0

ssl._create_default_https_context = ssl._create_stdlib_context



url = r"https://www.espn.com/nhl/standings/_/group/league"


htmlLines = urlopen(url).read().decode("utf-8").split()

standings = []

#data-idx="0"

itemRegEx = r'title="(\w+)'

for line in htmlLines:
    matcher = re.search(itemRegEx, line)
    if matcher is not None:
        team = matcher.group(1)
        if len(team) == 3:  
            standings.append(team)  
            #print(team)  

print('')

place  = int(input('Enter position to look for: '))

while place != '':
    if place < 33 and place >0:
        print( 'Team in', place,'is', standings[place-1])
        try:
            place  = int(input('Enter position to look for: '))
        except:
            break