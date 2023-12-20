import re
import validators

def youtube_url_validation(url):
    youtube_regex = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')

    youtube_regex_match = re.match(youtube_regex, url)
    if youtube_regex_match:
        return youtube_regex_match

    return youtube_regex_match

# print(youtube_url_validation('http://www.youtube.com/watch?v=5Y6HSHwhVlY'))

# youtube_urls_test = [
#     'http://www.youtube.com/watch?v=5Y6HSHwhVlY',
#     'http://youtu.be/5Y6HSHwhVlY', 
#     'http://www.youtube.com/embed/5Y6HSHwhVlY?rel=0" frameborder="0"',
#     'https://www.youtube-nocookie.com/v/5Y6HSHwhVlY?version=3&amp;hl=en_US',
#     'http://www.youtube.com/',
#     'http://www.youtube.com/?feature=ytca',
#     'http://www.youtube.com/watch?v=DFYRQ_zQ-gk#t=0m10s',
#     'http://www.youtube.com/embed/DFYRQ_zQ-gk?rel=0',
#     'www.youtube.com/watch?v=5Y6HSHwhVlY',
#     'youtube/5Y6HSHwhVlY']


PATTERN_URL = (
    r'(https?://)?(www\.)?'
    '(youtube|youtu|youtube-nocookie)\.(com|be)/'
    '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
)
def url_path_validation(url):
        pattern_url_match = re.match(PATTERN_URL, url)
        return bool(pattern_url_match)
# print(url_path_validation('www.youtube.com/watch?v=5Y6HSHwhVlY'))


print(validators.url('www.youtube.com/embed/DFYRQ_zQ-gk?rel=0'))