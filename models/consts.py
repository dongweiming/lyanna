K_POST = 1001
K_COMMENT = 1002
K_STATUS = 1003
K_ACTIVITY = 1004
K_CARD = 1005
K_FAVORITE = 1006

K_DOUBAN = 0
K_METACRITIC = 1
K_OTHER = 9

ONE_MINUTE = 60
ONE_HOUR = ONE_MINUTE * 60
ONE_DAY = ONE_HOUR * 24

T_MOVIE = 'movie'
T_BOOK = 'book'
T_GAME = 'game'

SUBDOMAIN_MAP = {
    T_MOVIE: 'movie',
    T_BOOK: 'book',
    T_GAME: 'www'
}

PERMALINK_TYPES = ('id', 'slug', 'title')
STATIC_FILE_TYPES = ('jpg', 'png', 'webp', 'gif', 'mp4', 'css', 'js')

UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.83 Safari/537.36'  # noqa
