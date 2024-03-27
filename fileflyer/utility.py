import os, os.path
import re
import random
import string

from logging import getLogger
from datetime import datetime
from time import mktime

logger = getLogger(__name__)

def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choices(characters, k=length))

    return random_string

def resolve_folder_name(name):
    components = name.split(os.path.sep)

    for i in range(len(components)):
        component = components[i]
        matches = re.findall(r'\{(.+?)\}', component)

        for match in matches:
            logger.debug(f"Match: {match}")
            fullmatch = '{' + match + '}'

            if match.startswith('date'):
                if match.startswith('date:'):
                    dateformat = match[len('date:'):]
                else:
                    dateformat = '%Y-%m-%d'
                date_string = datetime.now().strftime(dateformat)
                component = component.replace(fullmatch, date_string)
            elif match == 'timestamp':
                timeinterval = str(int(mktime(datetime.now().timetuple())))
                component = component.replace(fullmatch, timeinterval)
            elif re.match(r'^X+$', match) is not None:
                count = len(match)
                random_string = generate_random_string(count)
                component = component.replace(fullmatch, random_string)
            else:
                logger.warn('Unsupported match format!')

        components[i] = component

    return os.path.sep.join(components)
