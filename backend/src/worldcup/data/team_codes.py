# maps full team names (like the kaggle csv uses) to short codes (like "ARG")
# pycountry handles most current countries automatically. historical/edge-case
# teams (old countries, disputed regions, etc) are hardcoded below since they
# don't exist in pycountry's current country list.

import pycountry

# manual overrides for teams pycountry can't resolve - mostly historical
# teams, name mismatches, or non-country entities that play international football
MANUAL_OVERRIDES = {
    "West Germany": "FRG",
    "East Germany": "GDR",
    "Germany DR": "GDR",
    "German DR": "GDR",
    "Soviet Union": "URS",
    "Czechoslovakia": "TCH",
    "Yugoslavia": "YUG",
    "Serbia and Montenegro": "SCG",
    "Zaire": "ZAI",
    "South Korea": "KOR",
    "North Korea": "PRK",
    "North Vietnam": "VDR",
    "Vietnam Republic": "VNM_OLD",
    "South Yemen": "YMD",
    "Yemen DPR": "YMD",
    "Ivory Coast": "CIV",
    "Cape Verde": "CPV",
    "United States": "USA",
    "United States Virgin Islands": "VIR",
    "England": "ENG",
    "Scotland": "SCO",
    "Wales": "WAL",
    "Northern Ireland": "NIR",
    "Republic of Ireland": "IRL",
    "Hong Kong": "HKG",
    "Chinese Taipei": "TPE",
    "Congo DR": "COD",
    "DR Congo": "COD",
    "Curacao": "CUW",
    "Turkey": "TUR",
    "Macau": "MAC",
    "Tahiti": "PYF",
}


def get_team_code(team_name: str) -> str:
    """turns a full team name into a short code. checks manual list first,
    then tries pycountry, then just gives up and returns the name uppercased
    so nothing crashes - we can add it to MANUAL_OVERRIDES later if we spot it."""

    if team_name in MANUAL_OVERRIDES:
        return MANUAL_OVERRIDES[team_name]

    try:
        match = pycountry.countries.search_fuzzy(team_name)
        return match[0].alpha_3
    except LookupError:
        return team_name.upper().replace(" ", "_")[:10]


def is_resolvable(team_name: str) -> bool:
    """returns True if we got a real code (manual override or pycountry match),
    False if it fell through to the giving-up fallback. used to filter out
    non-FIFA entities (micronations, ConIFA teams, etc) from the dataset."""

    code = get_team_code(team_name)
    fallback = team_name.upper().replace(" ", "_")[:10]
    return team_name in MANUAL_OVERRIDES or code != fallback
