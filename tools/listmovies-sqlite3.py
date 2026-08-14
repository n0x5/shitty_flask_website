#!/usr/bin/env python

"""
Movie scanner.

IMDb:
    Reads metadata from local imdb.db.

TMDB:
    Scrapes the TMDB website for plot summaries.

Box Office Mojo:
    Scrapes Box Office Mojo for box office information.

The NFO file must contain an IMDb URL such as:

    https://www.imdb.com/title/tt0133093/

The script extracts:

    tt0133093

IMDb metadata is read locally from imdb.db.

TMDB is accessed through the website only.
No TMDB API is used.

No requests are made to imdb.com.

TMDB summaries are stored locally in movies.db in:

    tmdb_summary

Existing movies are updated when the script is run again.

IMPORTANT:

There is intentionally NO movie_catalog SQLite VIEW.

SQLite does not allow a persistent view in movies.db to
reference tables in an attached imdb.db.
"""


import os
import re
import time
import sqlite3
import traceback

from random import randint
from urllib.parse import quote_plus, urljoin

import requests
from bs4 import BeautifulSoup


# =============================================================================
# Configuration
# =============================================================================

cwd = r'F:\archive\xvid-scan'

number = 0


# =============================================================================
# Database paths
# =============================================================================

sql_db = os.path.join(
    os.path.dirname(__file__),
    '..',
    'databases',
    'movies.db'
)

imdb_db = r'C:\dev\imdb\imdb.db'


# =============================================================================
# Website configuration
# =============================================================================

HEADERS = {
    'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 '
        '(KHTML, like Gecko) '
        'Chrome/120.0.0.0 Safari/537.36',

    'Accept-Language':
        'en-US,en;q=0.9'
}


TMDB_BASE_URL = 'https://www.themoviedb.org'

BOXOFFICE_BASE_URL = (
    'https://www.boxofficemojo.com'
)


# =============================================================================
# Check IMDb database
# =============================================================================

if not os.path.exists(imdb_db):

    raise FileNotFoundError(
        "IMDb database not found:\n"
        f"{imdb_db}\n\n"
        "Run the IMDb database importer first."
    )


# =============================================================================
# Open movies database
# =============================================================================

conn = sqlite3.connect(
    sql_db
)

cur = conn.cursor()


# =============================================================================
# Attach IMDb database
#
# This is only for the current Python connection.
#
# We do NOT create a persistent view using imdb.* because SQLite does not
# allow persistent views in one database to reference an attached database.
# =============================================================================

cur.execute(
    "ATTACH DATABASE ? AS imdb",
    (imdb_db,)
)


# =============================================================================
# Create movies table
# =============================================================================

cur.execute(
    '''
    CREATE TABLE IF NOT EXISTS movies
    (
        release TEXT UNIQUE,
        grp TEXT,
        genre TEXT,
        format TEXT,
        imdb TEXT,
        tmdb_summary TEXT,
        dated DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    '''
)

conn.commit()


# =============================================================================
# Upgrade an existing movies table
#
# If the table already existed before tmdb_summary was added,
# add the column without destroying the existing data.
# =============================================================================

columns = [
    row[1]
    for row in cur.execute(
        "PRAGMA table_info(movies)"
    ).fetchall()
]


if 'tmdb_summary' not in columns:

    print(
        'Adding tmdb_summary column...'
    )

    cur.execute(
        '''
        ALTER TABLE movies
        ADD COLUMN tmdb_summary TEXT
        '''
    )

    conn.commit()


# =============================================================================
# Check required IMDb tables
# =============================================================================

required_imdb_tables = [
    'title_basics',
    'title_ratings',
    'title_crew',
    'title_principals',
    'name_basics'
]


for table in required_imdb_tables:

    result = cur.execute(
        '''
        SELECT 1
        FROM imdb.sqlite_master
        WHERE type = 'table'
        AND name = ?
        ''',
        (table,)
    ).fetchone()


    if result is None:

        raise RuntimeError(
            f"Required IMDb table '{table}' "
            f"was not found in {imdb_db}"
        )


# =============================================================================
# IMDb ID extraction
# =============================================================================

def imdburl2(fn):

    """
    Extract an IMDb ID from an NFO file.

    Example:

        https://www.imdb.com/title/tt0133093/

    returns:

        tt0133093
    """

    try:

        with open(
            fn,
            'r',
            encoding='utf-8',
            errors='ignore'
        ) as filn2:

            contents = filn2.read()

    except Exception as e:

        print(
            'Could not read NFO:',
            fn,
            e
        )

        return None


    match = re.search(
        r'imdb\.com/(?:title/)?(tt\d{6,12})',
        contents,
        re.IGNORECASE
    )


    if match:

        return match.group(1)


    return None


def imdburl(fn):

    return imdburl2(fn)


# =============================================================================
# Genre extraction from NFO
# =============================================================================

def genrs(fn):

    genrelist = [
        'romance',
        'comedy',
        'animation',
        'mystery',
        'documentary',
        'crime',
        'family',
        'sport',
        'biography',
        'history',
        'western',
        'sci-fi',
        'horror',
        'adventure',
        'drama',
        'fantasy',
        'thriller',
        'action'
    ]


    try:

        with open(
            fn,
            'r',
            encoding='utf-8',
            errors='ignore'
        ) as filn:

            for genres in filn:

                if 'genre' in genres.lower():

                    output = [
                        item.title()
                        for item in genrelist
                        if item in genres.lower()
                    ]


                    return ', '.join(
                        repr(e).replace("'", "")
                        for e in output
                    )

    except Exception:

        pass


    return ''


# =============================================================================
# Normalize a title for comparison
# =============================================================================

def normalize_title(title):

    if not title:

        return ''


    title = title.lower()


    title = re.sub(
        r'[^a-z0-9]+',
        ' ',
        title
    )


    return ' '.join(
        title.split()
    )


# =============================================================================
# Get an existing TMDB summary
# =============================================================================

def get_saved_tmdb_summary(imdb_id):

    if not imdb_id:

        return ''


    row = cur.execute(
        '''
        SELECT tmdb_summary

        FROM movies

        WHERE imdb = ?

        AND tmdb_summary IS NOT NULL

        AND tmdb_summary != ''

        LIMIT 1
        ''',
        (imdb_id,)
    ).fetchone()


    if row:

        return row[0]


    return ''


# =============================================================================
# Find TMDB movie page
# =============================================================================

def get_tmdb_page(
    title,
    year=None
):

    """
    Search the TMDB website by movie title.

    We use the title and year from the local IMDb database rather
    than trying to search TMDB for the IMDb tt... ID.

    Returns the TMDB movie URL.
    """

    if not title:

        return None


    print(
        'Searching TMDB website:',
        title,
        year
    )


    search_url = (
        TMDB_BASE_URL
        + '/search/movie?query='
        + quote_plus(title)
    )


    try:

        response = requests.get(
            search_url,
            headers=HEADERS,
            timeout=30
        )

        response.raise_for_status()

    except requests.RequestException as e:

        print(
            'TMDB search failed:',
            e
        )

        return None


    soup = BeautifulSoup(
        response.text,
        'html.parser'
    )


    # =========================================================================
    # Find movie links
    # =========================================================================

    links = soup.find_all(
        'a',
        href=re.compile(
            r'^/movie/\d+'
        )
    )


    if not links:

        print(
            'No TMDB movie results found:',
            title
        )

        return None


    wanted_title = normalize_title(
        title
    )


    wanted_year = ''


    if year:

        wanted_year = str(
            year
        )


    # =========================================================================
    # Remove duplicate links
    # =========================================================================

    candidates = []


    seen = set()


    for link in links:

        href = link.get(
            'href'
        )


        if not href:

            continue


        movie_url = urljoin(
            TMDB_BASE_URL,
            href
        )


        if movie_url in seen:

            continue


        seen.add(
            movie_url
        )


        candidates.append(
            (
                movie_url,
                link
            )
        )


    # =========================================================================
    # First pass:
    #
    # Try to match both title and year.
    # =========================================================================

    for movie_url, link in candidates:

        if link.parent:

            result_text = link.parent.get_text(
                ' ',
                strip=True
            )

        else:

            result_text = link.get_text(
                ' ',
                strip=True
            )


        normalized_result = normalize_title(
            result_text
        )


        title_match = (
            wanted_title in normalized_result
            or normalized_result in wanted_title
        )


        year_match = True


        if wanted_year:

            year_match = (
                wanted_year in result_text
            )


        if title_match and year_match:

            print(
                'TMDB match:',
                movie_url
            )

            return movie_url


    # =========================================================================
    # Second pass:
    #
    # Title-only match.
    # =========================================================================

    for movie_url, link in candidates:

        if link.parent:

            result_text = link.parent.get_text(
                ' ',
                strip=True
            )

        else:

            result_text = link.get_text(
                ' ',
                strip=True
            )


        normalized_result = normalize_title(
            result_text
        )


        if (
            wanted_title in normalized_result
            or normalized_result in wanted_title
        ):

            print(
                'TMDB title match:',
                movie_url
            )

            return movie_url


    # =========================================================================
    # Third pass:
    #
    # If the search page doesn't expose enough useful text, inspect
    # the candidate pages and compare their title/year.
    # =========================================================================

    checked = set()


    for movie_url, link in candidates:

        if movie_url in checked:

            continue


        checked.add(
            movie_url
        )


        try:

            movie_response = requests.get(
                movie_url,
                headers=HEADERS,
                timeout=30
            )


            if movie_response.status_code != 200:

                continue


        except requests.RequestException:

            continue


        movie_soup = BeautifulSoup(
            movie_response.text,
            'html.parser'
        )


        # -------------------------------------------------------------
        # Get page title
        # -------------------------------------------------------------

        page_title = ''


        title_element = movie_soup.find(
            'title'
        )


        if title_element:

            page_title = title_element.get_text(
                ' ',
                strip=True
            )


        normalized_page_title = normalize_title(
            page_title
        )


        if wanted_title in normalized_page_title:

            if (
                not wanted_year
                or wanted_year in page_title
            ):

                print(
                    'TMDB page match:',
                    movie_url
                )

                return movie_url


    print(
        'Could not find TMDB page:',
        title,
        year
    )


    return None


# =============================================================================
# Get plot summary from TMDB website
# =============================================================================

def get_tmdb_summary(
    title,
    year=None
):

    """
    Scrape the movie overview from TMDB.

    No TMDB API is used.
    """

    if not title:

        return ''


    tmdb_url = get_tmdb_page(
        title,
        year
    )


    if not tmdb_url:

        return ''


    print(
        'Reading TMDB:',
        tmdb_url
    )


    try:

        response = requests.get(
            tmdb_url,
            headers=HEADERS,
            timeout=30
        )

        response.raise_for_status()

    except requests.RequestException as e:

        print(
            'TMDB page request failed:',
            e
        )

        return ''


    soup = BeautifulSoup(
        response.text,
        'html.parser'
    )


    # =========================================================================
    # Method 1:
    #
    # Current/common TMDB overview selector.
    # =========================================================================

    selectors = [
        '[data-testid="movie-overview"]',
        '.overview',
        '.header_info .overview',
        '.overview p'
    ]


    for selector in selectors:

        element = soup.select_one(
            selector
        )


        if element:

            summary = element.get_text(
                ' ',
                strip=True
            )


            if len(summary) > 20:

                print(
                    'TMDB summary found.'
                )

                return summary


    # =========================================================================
    # Method 2:
    #
    # Find any element whose class contains "overview".
    # =========================================================================

    for element in soup.find_all(
        class_=re.compile(
            r'overview',
            re.IGNORECASE
        )
    ):

        summary = element.get_text(
            ' ',
            strip=True
        )


        if len(summary) > 20:

            print(
                'TMDB summary found.'
            )

            return summary


    # =========================================================================
    # Method 3:
    #
    # Look for a meta description.
    # =========================================================================

    meta = soup.find(
        'meta',
        attrs={
            'name': 'description'
        }
    )


    if meta:

        summary = meta.get(
            'content',
            ''
        ).strip()


        if len(summary) > 40:

            print(
                'TMDB summary found in meta description.'
            )

            return summary


    # =========================================================================
    # Method 4:
    #
    # JSON-LD description.
    # =========================================================================

    scripts = soup.find_all(
        'script',
        attrs={
            'type': 'application/ld+json'
        }
    )


    for script in scripts:

        text = script.get_text(
            strip=True
        )


        if not text:

            continue


        match = re.search(
            r'"description"\s*:\s*"((?:\\.|[^"\\])*)"',
            text,
            re.IGNORECASE
        )


        if match:

            summary = match.group(1)


            summary = (
                summary
                .replace(
                    '\\"',
                    '"'
                )
                .replace(
                    '\\n',
                    ' '
                )
                .replace(
                    '\\r',
                    ' '
                )
            )


            summary = summary.strip()


            if len(summary) > 20:

                print(
                    'TMDB summary found in JSON-LD.'
                )

                return summary


    print(
        'No TMDB summary found:',
        title
    )


    return ''


# =============================================================================
# Get IMDb information from local imdb.db
# =============================================================================

def get_info(imdb_id):

    """
    Get IMDb information from the local IMDb database.

    Returns:

        title
        directors
        actors
        genres
        cast
        summary
        year
    """

    print(
        'Getting IMDb information from local database:',
        imdb_id
    )


    # =========================================================================
    # Basic title information
    # =========================================================================

    movie = cur.execute(
        '''
        SELECT

            b.tconst,
            b.primaryTitle,
            b.originalTitle,
            b.titleType,
            b.startYear,
            b.endYear,
            b.genres,
            r.averageRating,
            r.numVotes

        FROM imdb.title_basics AS b

        LEFT JOIN imdb.title_ratings AS r
            ON r.tconst = b.tconst

        WHERE b.tconst = ?
        ''',
        (imdb_id,)
    ).fetchone()


    if movie is None:

        print(
            'IMDb ID not found:',
            imdb_id
        )

        return (
            '',
            '',
            [],
            [],
            [],
            '',
            ''
        )


    (
        tconst,
        title,
        original_title,
        title_type,
        start_year,
        end_year,
        genres,
        rating,
        votes
    ) = movie


    # =========================================================================
    # Directors
    # =========================================================================

    crew = cur.execute(
        '''
        SELECT
            directors,
            writers

        FROM imdb.title_crew

        WHERE tconst = ?
        ''',
        (imdb_id,)
    ).fetchone()


    directors = []


    if crew and crew[0]:

        director_ids = [
            x.strip()
            for x in crew[0].split(',')
            if x.strip()
        ]


        if director_ids:

            placeholders = ','.join(
                '?'
                for _ in director_ids
            )


            rows = cur.execute(
                f'''
                SELECT
                    nconst,
                    primaryName

                FROM imdb.name_basics

                WHERE nconst IN ({placeholders})
                ''',
                director_ids
            ).fetchall()


            name_lookup = {
                row[0]: row[1]
                for row in rows
            }


            for director_id in director_ids:

                name = name_lookup.get(
                    director_id
                )


                if name:

                    directors.append(
                        name
                    )


    directors = list(
        dict.fromkeys(
            directors
        )
    )


    director_string = ', '.join(
        directors
    )


    # =========================================================================
    # Actors
    # =========================================================================

    actor_rows = cur.execute(
        '''
        SELECT

            p.nconst,
            p.ordering,
            p.category

        FROM imdb.title_principals AS p

        WHERE p.tconst = ?

        AND p.category IN (
            'actor',
            'actress'
        )

        ORDER BY p.ordering
        ''',
        (imdb_id,)
    ).fetchall()


    actors = []


    if actor_rows:

        actor_ids = [
            row[0]
            for row in actor_rows
        ]


        placeholders = ','.join(
            '?'
            for _ in actor_ids
        )


        names = cur.execute(
            f'''
            SELECT

                nconst,
                primaryName

            FROM imdb.name_basics

            WHERE nconst IN ({placeholders})
            ''',
            actor_ids
        ).fetchall()


        name_lookup = {
            row[0]: row[1]
            for row in names
        }


        for nconst, ordering, category in actor_rows:

            name = name_lookup.get(
                nconst
            )


            if name:

                actors.append(
                    name
                )


    actors = list(
        dict.fromkeys(
            actors
        )
    )


    actors = actors[:20]


    # Store actors as:

    # ['Actor One', 'Actor Two']

    actors_string = str(
        actors
    )


    # =========================================================================
    # Genres
    #
    # IMDb stores:
    #
    #     Action,Adventure,Sci-Fi
    #
    # We store:
    #
    #     ['Action', 'Adventure', 'Sci-Fi']
    # =========================================================================

    imdb_genres = []


    if genres:

        imdb_genres = [
            genre.strip()
            for genre in genres.split(',')
            if genre.strip()
        ]


    imdb_genres_string = str(
        imdb_genres
    )


    # =========================================================================
    # Year
    # =========================================================================

    year = ''


    if start_year is not None:

        year = str(
            start_year
        )


    # =========================================================================
    # TMDB summary
    #
    # First use a saved summary.
    #
    # If there isn't one, search TMDB by title/year.
    # =========================================================================

    summary = get_saved_tmdb_summary(
        imdb_id
    )


    if summary:

        print(
            'Using saved TMDB summary.'
        )

    else:

        summary = get_tmdb_summary(
            title,
            year
        )


    # =========================================================================
    # Cast
    # =========================================================================

    cast = actors_string


    # =========================================================================
    # Display
    # =========================================================================

    print(
        'IMDb:',
        imdb_id
    )

    print(
        'Title:',
        title
    )

    print(
        'Year:',
        year
    )

    print(
        'Rating:',
        rating
    )

    print(
        'Votes:',
        votes
    )

    print(
        'Director:',
        director_string
    )

    print(
        'Actors:',
        actors_string
    )

    print(
        'Genres:',
        imdb_genres_string
    )

    print(
        'Summary:',
        summary
    )


    return (
        title,
        director_string,
        actors_string,
        imdb_genres_string,
        cast,
        summary,
        year
    )


# =============================================================================
# Store / update movie
# =============================================================================

def store(
    release,
    grp,
    genre,
    imdb_id,
    summary
):

    """
    Insert or update a movie.

    Existing movies are updated.

    An empty TMDB summary will NOT overwrite an existing summary.
    """

    existing = cur.execute(
        '''
        SELECT release
        FROM movies
        WHERE release = ?
        ''',
        (release,)
    ).fetchone()


    if existing:

        if summary:

            cur.execute(
                '''
                UPDATE movies

                SET
                    grp = ?,
                    genre = ?,
                    format = ?,
                    imdb = ?,
                    tmdb_summary = ?

                WHERE release = ?
                ''',
                (
                    grp,
                    genre,
                    file7,
                    imdb_id,
                    summary,
                    release
                )
            )

        else:

            cur.execute(
                '''
                UPDATE movies

                SET
                    grp = ?,
                    genre = ?,
                    format = ?,
                    imdb = ?

                WHERE release = ?
                ''',
                (
                    grp,
                    genre,
                    file7,
                    imdb_id,
                    release
                )
            )


    else:

        cur.execute(
            '''
            INSERT INTO movies
            (
                release,
                grp,
                genre,
                format,
                imdb,
                tmdb_summary
            )

            VALUES (?, ?, ?, ?, ?, ?)
            ''',
            (
                release,
                grp,
                genre,
                file7,
                imdb_id,
                summary
            )
        )


    conn.commit()


# =============================================================================
# Get combined movie information
# =============================================================================

def get_movie_catalog(imdb_id):

    """
    Return local movie information combined with IMDb information.

    This replaces the old movie_catalog VIEW.

    It works because imdb.db is attached to the current connection.
    """

    row = cur.execute(
        '''
        SELECT

            m.release,
            m.grp,
            m.genre AS folder_genre,
            m.format,
            m.imdb,
            m.tmdb_summary,
            m.dated,

            b.primaryTitle AS title,
            b.originalTitle,
            b.titleType,

            b.startYear AS year,
            b.endYear,
            b.runtimeMinutes,

            b.genres AS imdb_genres,

            r.averageRating,
            r.numVotes,

            c.directors,
            c.writers

        FROM movies AS m

        LEFT JOIN imdb.title_basics AS b
            ON b.tconst = m.imdb

        LEFT JOIN imdb.title_ratings AS r
            ON r.tconst = m.imdb

        LEFT JOIN imdb.title_crew AS c
            ON c.tconst = m.imdb

        WHERE m.imdb = ?
        ''',
        (imdb_id,)
    ).fetchone()


    return row


# =============================================================================
# Box Office Mojo
# =============================================================================

def get_info_box(url):

    headers = {
        'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; WOW64; '
            'rv:47.0) Gecko/20100101 Firefox/47.0'
    }


    print(
        'Getting Box Office Mojo:',
        url
    )


    response = requests.get(
        url,
        headers=headers,
        timeout=30
    )


    soup = BeautifulSoup(
        response.text,
        'html.parser'
    )


    imdb_id_match = re.search(
        r'(tt\d{6,12})',
        url
    )


    table = soup.find(
        'main'
    )


    if table is None:

        raise RuntimeError(
            'Box Office Mojo page not found'
        )


    title_element = table.find(
        'h1',
        attrs={
            'class':
                'a-size-extra-large'
        }
    )


    if title_element is None:

        raise RuntimeError(
            'Could not find Box Office Mojo title'
        )


    title = title_element.get_text()


    table2 = table.find(
        'div',
        attrs={
            'class':
                'a-section a-spacing-none '
                'mojo-gutter mojo-summary-table'
        }
    )


    if table2 is None:

        raise RuntimeError(
            'Could not find Box Office Mojo summary table'
        )


    distributor2 = table2.find(
        'div',
        attrs={
            'class':
                'a-section a-spacing-none '
                'mojo-summary-values '
                'mojo-hidden-from-mobile'
        }
    )


    if distributor2 is None:

        raise RuntimeError(
            'Could not find distributor information'
        )


    distributor_spans = distributor2.find_all(
        'span'
    )


    distributor = ''


    if len(distributor_spans) > 1:

        distributor = (
            distributor_spans[1]
            .get_text(
                strip=True
            )
            .replace(
                'See full company information',
                ''
            )
            .strip()
        )


    rel_date = ''


    if len(distributor_spans) > 6:

        rel_date = (
            distributor_spans[6]
            .get_text(
                strip=True
            )
        )


    rel1 = table.find(
        'table',
        attrs={
            'class':
                'a-bordered a-horizontal-stripes '
                'a-size-base-plus'
        }
    )


    if rel1 is None:

        return


    lists = rel1.find(
        'a',
        href=re.compile(
            r'/release'
        )
    )


    theaters_max3 = ''
    theaters_openwide = ''
    rl_id = None


    if lists and 'Domestic' in str(lists):

        rl_match = re.search(
            r'(rl\d{7,12})',
            str(
                lists.get(
                    'href',
                    ''
                )
            )
        )


        if rl_match:

            rl_id = rl_match.group(1)


        url2 = (
            BOXOFFICE_BASE_URL
            + lists['href']
            + '/weekend/'
        )


        print(
            'Fetching Box Office weekend:'
        )


        response2 = requests.get(
            url2,
            headers=headers,
            timeout=30
        )


        soup2 = BeautifulSoup(
            response2.text,
            'html.parser'
        )


        table2 = soup2.find(
            'div',
            attrs={
                'class':
                    'a-section a-spacing-none '
                    'mojo-summary-values '
                    'mojo-hidden-from-mobile'
            }
        )


        if table2:

            for item in table2.find_all(
                'div',
                attrs={
                    'class':
                        'a-section a-spacing-none'
                }
            ):

                item_text = str(
                    item
                ).replace(
                    '\n',
                    ''
                )


                if (
                    'theaters' in item_text
                    and 'Opening' in item_text
                ):

                    match = re.search(
                        r'(\d{0,4}\,\d{2,5}|\d{0,9000})'
                        r'\s+theaters',
                        item_text
                    )


                    if match:

                        theaters_max3 = (
                            match.group(1)
                            .replace(
                                'theaters',
                                ''
                            )
                            .strip()
                        )


                if (
                    'theaters' in item_text
                    and 'Widest' in item_text
                ):

                    match = re.search(
                        r'(\d{0,4}\,\d{2,5}|\d{0,9000})'
                        r'\s+theaters',
                        item_text
                    )


                    if match:

                        theaters_openwide = (
                            match.group(1)
                            .replace(
                                'theaters',
                                ''
                            )
                            .strip()
                        )


    alt_theaters = theaters_openwide


    stuff = (
        title,
        theaters_max3,
        theaters_openwide,
        alt_theaters,
        rel_date,
        distributor,
        rl_id,
        imdb_id_match.group(1)
        if imdb_id_match
        else None
    )


    # Only insert if the table exists.

    table_exists = cur.execute(
        '''
        SELECT 1
        FROM sqlite_master
        WHERE type = 'table'
        AND name = 'boxoffice'
        '''
    ).fetchone()


    if table_exists:

        cur.execute(
            '''
            INSERT INTO boxoffice
            (
                title,
                wide_theatersopen,
                wide_theaters,
                alt_theaters,
                alt_releasedate,
                alt_distributor,
                rlid,
                imdbid
            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            stuff
        )


        conn.commit()


    print(
        stuff
    )


# =============================================================================
# Scan movie folders
# =============================================================================

for subdir, dirs, files in os.walk(cwd):

    for fn in files:

        if not fn.lower().endswith(
            '.nfo'
        ):

            continue


        try:

            # =================================================================
            # NFO path
            # =================================================================

            file2 = os.path.join(
                subdir,
                fn
            )


            # =================================================================
            # Folder name
            # =================================================================

            basenm2 = os.path.basename(
                subdir
            )


            file6 = '[]'.join(
                basenm2.split('-')[-1:]
            )


            file7 = '[]'.join(
                basenm2.split('.')[-1:]
            ).split('-')[0]


            # =================================================================
            # Banned folders
            # =================================================================

            banned = [
                'cd1',
                'cd2',
                'sample',
                'vobsub',
                'subs',
                'proof',
                'prooffix',
                'syncfix'
            ]


            # =================================================================
            # Get IMDb ID
            # =================================================================

            imdb_id = imdburl2(
                file2
            )


            print()
            print(
                '=' * 70
            )


            print(
                'NFO:',
                file2
            )


            print(
                'IMDb ID:',
                imdb_id
            )


            # =================================================================
            # IMDb information + TMDB summary
            # =================================================================

            if imdb_id:

                try:

                    imdb_info = get_info(
                        imdb_id
                    )


                except Exception as e:

                    print(
                        'IMDb/TMDB lookup failed:',
                        e
                    )


                    traceback.print_exc()


                    imdb_info = (
                        '',
                        '',
                        [],
                        [],
                        [],
                        '',
                        ''
                    )


            else:

                print(
                    'No IMDb ID found.'
                )


                imdb_info = (
                    '',
                    '',
                    [],
                    [],
                    [],
                    '',
                    ''
                )


            # =================================================================
            # Box Office Mojo
            # =================================================================

            if imdb_id:

                try:

                    boxoffice_url = (
                        BOXOFFICE_BASE_URL
                        + '/title/'
                        + imdb_id
                    )


                    get_info_box(
                        boxoffice_url
                    )


                except Exception as e:

                    print(
                        'Film not in Box Office Mojo:',
                        e
                    )


            # =================================================================
            # Store movie
            # =================================================================

            if (
                basenm2.lower().split('.')[0]
                not in banned
            ):

                try:

                    store(
                        basenm2,
                        file6,
                        genrs(file2),
                        imdb_id,
                        imdb_info[5]
                    )


                except Exception as e:

                    print(
                        'Could not store movie:',
                        e
                    )


                    traceback.print_exc()


            number += 1


            # =================================================================
            # Delay for online requests
            # =================================================================

            time.sleep(
                randint(
                    2,
                    4
                )
            )


        except Exception as e:

            print(
                'ERROR:',
                e
            )


            traceback.print_exc()


            with open(
                'err.txt',
                'a',
                encoding='utf-8'
            ) as fp:

                fp.write(
                    subdir
                    + ' '
                    + fn
                    + '\n'
                )


# =============================================================================
# Close database
# =============================================================================

conn.close()


print()
print(
    '=' * 70
)

print(
    'Finished.'
)

print(
    'Movies scanned:',
    number
)