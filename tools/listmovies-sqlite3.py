# IMDb database version of the movie scanner

#!/usr/bin/env python

"""
Create an sqlite db of movies in a folder.

Recursive scan of folders.

IMDb information is read from the local imdb.db database created
by the IMDb dataset importer.

The .nfo file still needs to contain an IMDb URL such as:

    https://www.imdb.com/title/tt0133093/

The script extracts tt0133093 and looks it up locally.

No requests to imdb.com are made.

Box Office Mojo is still queried separately by get_info_box().
"""

import os
import re
import time
import sqlite3
import traceback
from random import randint


# ============================================================================
# Configuration
# ============================================================================

today = time.strftime("__%m_%Y_%H_%M_%S")

cwd = r'F:\archive\xvid-scan'

number = 0


# Movie database created by this script
sql_db = os.path.join(
    os.path.dirname(__file__),
    '..',
    'databases',
    'movies.db'
)


# ---------------------------------------------------------------------------
# IMDb database created by the IMDb importer
#
# Change this path if imdb.db lives somewhere else.
# ---------------------------------------------------------------------------

imdb_db = r'C:\dev\imdb\imdb.db'


# ============================================================================
# Open movie database
# ============================================================================

conn = sqlite3.connect(sql_db)
cur = conn.cursor()

cur.execute(
    '''
    CREATE TABLE IF NOT EXISTS movies
    (
        release text unique,
        grp text,
        genre text,
        format text,
        imdb text,
        title text,
        director text,
        mainactors text,
        infogenres text,
        inforest text,
        infosummary text,
        year text,
        dated datetime DEFAULT CURRENT_TIMESTAMP
    )
    '''
)

conn.commit()


# ============================================================================
# Open IMDb database
# ============================================================================

if not os.path.exists(imdb_db):
    raise FileNotFoundError(
        "IMDb database not found:\n"
        f"{imdb_db}\n\n"
        "Run the IMDb database importer first."
    )


imdb_conn = sqlite3.connect(
    f'file:{imdb_db}?mode=ro',
    uri=True
)

imdb_cur = imdb_conn.cursor()


# ============================================================================
# Check that the expected IMDb tables exist
# ============================================================================

def check_imdb_database():

    required_tables = [
        'title_basics',
        'title_crew',
        'title_principals',
        'title_ratings',
        'name_basics',
    ]

    for table in required_tables:

        result = imdb_cur.execute(
            """
            SELECT 1
            FROM sqlite_master
            WHERE type = 'table'
              AND name = ?
            """,
            (table,)
        ).fetchone()

        if result is None:
            raise RuntimeError(
                f"Required IMDb table '{table}' "
                f"does not exist in:\n{imdb_db}"
            )


check_imdb_database()


# ============================================================================
# IMDb ID extraction
# ============================================================================

def imdburl2(fn):

    """
    Extract an IMDb ID from an .nfo file.

    Example:

        https://www.imdb.com/title/tt0133093/

    returns:

        tt0133093
    """

    try:

        with open(
            fn,
            "r",
            encoding="utf-8",
            errors="ignore"
        ) as filn2:

            contents = filn2.read()

    except Exception:

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

    """
    Return the IMDb ID from an .nfo file.

    Kept for compatibility with the original script.
    """

    return imdburl2(fn)


# ============================================================================
# Genre extraction from local NFO
# ============================================================================

def genrs(fn):

    genrelist = [
        "romance",
        "comedy",
        "animation",
        "mystery",
        "documentary",
        "crime",
        "family",
        "sport",
        "biography",
        "history",
        "western",
        "sci-fi",
        "horror",
        "adventure",
        "drama",
        "fantasy",
        "thriller",
        "action"
    ]

    try:

        with open(
            fn,
            "r",
            encoding="utf-8",
            errors="ignore"
        ) as filn:

            for genres in filn:

                if "genre" in genres.lower():

                    output = [
                        item.title()
                        for item in genrelist
                        if item in genres.lower()
                    ]

                    return ", ".join(
                        repr(e).replace("'", "")
                        for e in output
                    )

    except Exception:

        pass

    return ""


# ============================================================================
# IMDb lookup
# ============================================================================

def get_info(imdb_id):

    """
    Get movie information from the local IMDb SQLite database.

    Returns:

        title
        director
        actors
        genres
        cast
        summary
        year

    The public IMDb datasets do not contain the webpage description,
    keywords, poster URL, or content rating that the old scraper obtained,
    so summary is currently empty.
    """

    print(
        "Getting IMDb information from local database:",
        imdb_id
    )


    # ------------------------------------------------------------------------
    # Basic title information + rating
    # ------------------------------------------------------------------------

    movie = imdb_cur.execute(
        """
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
        FROM title_basics AS b

        LEFT JOIN title_ratings AS r
            ON r.tconst = b.tconst

        WHERE b.tconst = ?
        """,
        (imdb_id,)
    ).fetchone()


    if movie is None:

        print(
            "IMDb ID not found in local database:",
            imdb_id
        )

        return (
            "",
            "",
            "",
            "",
            [],
            "",
            ""
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


    # ------------------------------------------------------------------------
    # Director(s)
    #
    # title_crew.directors contains a comma-separated list of nconst IDs.
    # Resolve those IDs against name_basics.
    # ------------------------------------------------------------------------

    crew = imdb_cur.execute(
        """
        SELECT
            directors,
            writers
        FROM title_crew
        WHERE tconst = ?
        """,
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

            placeholders = ",".join(
                "?"
                for _ in director_ids
            )

            rows = imdb_cur.execute(
                f"""
                SELECT
                    nconst,
                    primaryName
                FROM name_basics
                WHERE nconst IN ({placeholders})
                ORDER BY primaryName
                """,
                director_ids
            ).fetchall()

            directors = [
                row[1]
                for row in rows
            ]


    director_string = ", ".join(
        directors
    )


    # ------------------------------------------------------------------------
    # Main actors
    #
    # IMDb principals contains categories such as:
    #
    #   actor
    #   actress
    #   self
    #   director
    #   writer
    #
    # We take actor/actress entries and resolve nconst through name_basics.
    # ------------------------------------------------------------------------

    actor_rows = imdb_cur.execute(
        """
        SELECT
            p.nconst,
            p.ordering,
            p.category
        FROM title_principals AS p
        WHERE p.tconst = ?
          AND p.category IN (
              'actor',
              'actress'
          )
        ORDER BY p.ordering
        """,
        (imdb_id,)
    ).fetchall()


    actors = []

    if actor_rows:

        actor_ids = [
            row[0]
            for row in actor_rows
        ]

        placeholders = ",".join(
            "?"
            for _ in actor_ids
        )

        names = imdb_cur.execute(
            f"""
            SELECT
                nconst,
                primaryName
            FROM name_basics
            WHERE nconst IN ({placeholders})
            """,
            actor_ids
        ).fetchall()

        name_lookup = {
            row[0]: row[1]
            for row in names
        }

        # Preserve IMDb's principal ordering.
        for nconst, ordering, category in actor_rows:

            name = name_lookup.get(
                nconst
            )

            if name:
                actors.append(name)


    # Remove duplicates while preserving order.

    actors = list(
        dict.fromkeys(actors)
    )


    # Limit to the main cast.

    actors = actors[:20]


    # ------------------------------------------------------------------------
    # IMDb genres
    # ------------------------------------------------------------------------

    imdb_genres = ""

    if genres:

        imdb_genres = genres.replace(
            ",",
            ", "
        )


    # ------------------------------------------------------------------------
    # Year
    # ------------------------------------------------------------------------

    year = ""

    if start_year is not None:
        year = str(start_year)


    # ------------------------------------------------------------------------
    # The public IMDb datasets don't contain the old webpage summary.
    # ------------------------------------------------------------------------

    summary = ""


    # ------------------------------------------------------------------------
    # Cast
    # ------------------------------------------------------------------------

    cast = actors.copy()


    # ------------------------------------------------------------------------
    # Print useful diagnostic information
    # ------------------------------------------------------------------------

    print(
        "IMDb:",
        imdb_id,
        "|",
        title,
        "|",
        year,
        "|",
        rating,
        "|",
        votes
    )

    print(
        "Director:",
        director_string
    )

    print(
        "Actors:",
        ", ".join(actors)
    )

    print(
        "Genres:",
        imdb_genres
    )


    return (
        title,
        director_string,
        actors,
        imdb_genres,
        cast,
        summary,
        year
    )


# ============================================================================
# Store movie
# ============================================================================

def store(
    release,
    grp,
    genre,
    title,
    director,
    mainactors,
    infogenres,
    inforest,
    infosummary,
    year
):

    imdb_id = imdburl(file2)


    print(
        '{} - {} - {} - {} - {} - {} - {} - {} - {} - {} - {} - {}'.format(
            basenm2,
            file6,
            genrs(file2),
            file7,
            imdb_id,
            str(imdb_info[0]).strip(),
            str(imdb_info[1]).strip(),
            str(imdb_info[2]).replace('\\n', ''),
            str(imdb_info[3]),
            str(imdb_info[4]),
            str(imdb_info[5]),
            str(imdb_info[6])
        )
    )


    cur.execute(
        '''
        INSERT OR IGNORE INTO movies
        (
            release,
            grp,
            genre,
            format,
            imdb,
            title,
            director,
            mainactors,
            infogenres,
            inforest,
            infosummary,
            year
        )
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        ''',

        (
            basenm2,
            file6,
            genrs(file2),
            file7,
            imdb_id,
            str(imdb_info[0]).strip(),
            str(imdb_info[1]).strip().replace(',', ''),
            str(imdb_info[2]).replace('\\n', '').strip(),
            str(imdb_info[3]).strip(),
            str(imdb_info[4]).strip(),
            str(imdb_info[5]).strip(),
            str(imdb_info[6])
        )
    )


    cur.connection.commit()


# ============================================================================
# Box Office Mojo
#
# This section is intentionally unchanged conceptually.
# It still gets data from Box Office Mojo, NOT IMDb.
# ============================================================================

def get_info_box(url):

    import requests
    from bs4 import BeautifulSoup

    headers = {
        'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; WOW64; '
            'rv:47.0) Gecko/20100101 Firefox/47.0'
    }

    print(
        'getting film:',
        url
    )

    response = requests.get(
        url,
        headers=headers
    )

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    imdb_id = re.search(
        r'(tt\d{6,12})',
        url
    )

    table = soup.find(
        'main'
    )

    if table is None:
        raise RuntimeError(
            "Box Office Mojo page not found"
        )

    title = table.find(
        'h1',
        attrs={
            'class':
                'a-size-extra-large'
        }
    ).get_text()

    table2 = table.find(
        'div',
        attrs={
            'class':
                'a-section a-spacing-none '
                'mojo-gutter mojo-summary-table'
        }
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

    distributor = distributor2.find_all(
        'span'
    )[1].get_text().replace(
        'See full company information\n\n',
        ''
    )

    rel_date = distributor2.find_all(
        'span'
    )[6].get_text()

    rel1 = table.find(
        'table',
        attrs={
            'class':
                'a-bordered a-horizontal-stripes '
                'a-size-base-plus'
        }
    )

    lists = rel1.find(
        'a',
        href=re.compile(
            r'\/release'
        )
    )

    theaters_max3 = ''
    theaters_openwide = ''

    if 'Domestic' in str(lists):

        rl_id = re.search(
            r'(rl\d{7,12})',
            str(lists['href'])
        )

        url2 = (
            'https://www.boxofficemojo.com'
            + lists['href']
            + '/weekend/'
        )

        print(
            'Fetching Boxoffice weekend:'
        )

        response2 = requests.get(
            url2,
            headers=headers
        )

        soup2 = BeautifulSoup(
            response2.text,
            "html.parser"
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

        for item in table2.find_all(
            'div',
            attrs={
                'class':
                    'a-section a-spacing-none'
            }
        ):

            if (
                'theaters' in str(item)
                and 'Opening' in str(item)
            ):

                match = re.search(
                    r'(\d{0,4}\,\d{2,5}|\d{0,9000})'
                    r'\s+theaters',
                    str(item).replace(
                        '\n',
                        ''
                    )
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
                'theaters' in str(item)
                and 'Widest' in str(item)
            ):

                match = re.search(
                    r'(\d{0,4}\,\d{2,5}|\d{0,9000})'
                    r'\s+theaters',
                    str(item).replace(
                        '\n',
                        ''
                    )
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
        rl_id.group(1),
        imdb_id.group(1)
    )


    # This assumes the boxoffice table already exists,
    # as in the original script.

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
        VALUES (?,?,?,?,?,?,?,?)
        ''',
        stuff
    )

    cur.connection.commit()

    print(
        stuff
    )


# ============================================================================
# Scan movie folders
# ============================================================================

for subdir, dirs, files in os.walk(cwd):

    for fn in files:

        if not fn.endswith(
            ".nfo"
        ):
            continue

        try:

            file2 = os.path.join(
                subdir,
                fn
            )

            basenm2 = os.path.basename(
                os.path.join(subdir)
            )

            file6 = "[]".join(
                basenm2.split('-')[-1:]
            )

            file7 = "[]".join(
                basenm2.split('.')[-1:]
            ).split('-')[0]

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


            # ----------------------------------------------------------------
            # Get IMDb ID from NFO
            # ----------------------------------------------------------------

            try:

                imdb_id = imdburl2(
                    file2
                )

            except Exception:

                imdb_id = None

                print(
                    'IMDb ID not in file'
                )


            print()
            print(
                'NFO:',
                file2
            )

            print(
                'IMDb ID:',
                imdb_id
            )


            # ----------------------------------------------------------------
            # Box Office Mojo
            #
            # This remains online because the local IMDb database does
            # not contain Box Office Mojo information.
            # ----------------------------------------------------------------

            if imdb_id:

                try:

                    boxoffice_url = (
                        'https://www.boxofficemojo.com/title/'
                        + imdb_id
                    )

                    print(
                        'Fetching Box Office Mojo:'
                    )

                    get_info_box(
                        boxoffice_url
                    )

                except Exception as e:

                    print(
                        'Film not in boxoffice:',
                        e
                    )


            # ----------------------------------------------------------------
            # IMDb information
            #
            # NO IMDb web request happens here.
            # ----------------------------------------------------------------

            if imdb_id:

                try:

                    imdb_info = get_info(
                        imdb_id
                    )

                except Exception as e:

                    print(
                        'IMDb database lookup failed:',
                        e
                    )

                    traceback.print_exc()

                    imdb_info = (
                        '',
                        '',
                        '',
                        '',
                        [],
                        '',
                        ''
                    )

            else:

                imdb_info = (
                    '',
                    '',
                    '',
                    '',
                    [],
                    '',
                    ''
                )


            # ----------------------------------------------------------------
            # Store movie
            # ----------------------------------------------------------------

            if (
                basenm2.lower().split('.')[0]
                not in banned
            ):

                try:

                    store(
                        basenm2,
                        file6,
                        genrs(file2),
                        imdb_info[0],
                        imdb_info[1],
                        imdb_info[2],
                        imdb_info[3],
                        imdb_info[4],
                        imdb_info[5],
                        str(imdb_info[6])
                    )

                except Exception as e:

                    print(
                        'Could not store movie:',
                        e
                    )

                    traceback.print_exc()


            number += 1


            # No reason to wait 15-20 seconds for IMDb anymore.
            #
            # Keep a very short delay because Box Office Mojo is
            # still queried above.

            r_int = randint(
                2,
                4
            )

            time.sleep(
                r_int
            )


        except Exception as e:

            print(
                e
            )

            traceback.print_exc()

            with open(
                'err.txt',
                'a'
            ) as fp:

                fp.write(
                    subdir
                    + ' '
                    + fn
                    + '\n'
                )


# ============================================================================
# Cleanup
# ============================================================================

imdb_conn.close()
conn.close()

print()
print(
    "Finished. Movies scanned:",
    number
)

