#!/usr/bin/env python3
"""Generate a world choropleth map of LSST TVS members by country."""

import os
import re
import math
import json
from collections import Counter
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from pathlib import Path

# --- Country TLD to ISO-3166 alpha-2 ---
TLD_TO_COUNTRY = {
    'de': 'Germany', 'fr': 'France', 'es': 'Spain', 'it': 'Italy',
    'nl': 'Netherlands', 'dk': 'Denmark', 'cz': 'Czech Republic',
    'pl': 'Poland', 'se': 'Sweden', 'fi': 'Finland', 'gr': 'Greece',
    'pt': 'Portugal', 'be': 'Belgium', 'at': 'Austria', 'hu': 'Hungary',
    'hr': 'Croatia', 'rs': 'Serbia', 'si': 'Slovenia', 'sk': 'Slovakia',
    'ro': 'Romania', 'bg': 'Bulgaria', 'lt': 'Lithuania', 'lv': 'Latvia',
    'ee': 'Estonia', 'ie': 'Ireland', 'no': 'Norway', 'ch': 'Switzerland',
    'uk': 'United Kingdom', 'ac.uk': 'United Kingdom',
    'au': 'Australia', 'nz': 'New Zealand', 'jp': 'Japan',
    'cn': 'China', 'tw': 'Taiwan', 'in': 'India', 'kr': 'South Korea',
    'za': 'South Africa', 'cl': 'Chile', 'br': 'Brazil', 'ar': 'Argentina',
    'mx': 'Mexico', 'co': 'Colombia', 'tr': 'Turkey', 'ru': 'Russia',
    'ge': 'Georgia', 'sg': 'Singapore', 'il': 'Israel', 'ir': 'Iran',
    'et': 'Ethiopia', 'rw': 'Rwanda', 'ke': 'Kenya', 'tz': 'Tanzania',
    'ug': 'Uganda', 'gh': 'Ghana', 'ng': 'Nigeria', 'ma': 'Morocco',
    'eg': 'Egypt', 'ae': 'United Arab Emirates', 'ca': 'Canada',
    'uantof.cl': 'Chile', 'udec.cl': 'Chile', 'puc.cl': 'Chile',
}

# Normalise the raw continent/country tags in the spreadsheet
CC_MAP = {
    'us': 'United States', 'usa': 'United States',
    'uk': 'United Kingdom',
    'au': 'Australia', 'aus': 'Australia', 'australia': 'Australia',
    'cl': 'Chile', 'chile': 'Chile',
    'sa': 'South Africa',
    'ar': 'Argentina', 'argentina': 'Argentina',
    'brazil': 'Brazil', 'br': 'Brazil',
    'india': 'India', 'in': 'India',
    'canada': 'Canada', 'ca': 'Canada',
    'korea': 'South Korea', 's. korea': 'South Korea', 's korea': 'South Korea',
    'taiwan': 'Taiwan', 'tw': 'Taiwan',
    'nz': 'New Zealand', 'new zealand': 'New Zealand',
    'turkey': 'Turkey', 'tr': 'Turkey',
    'china': 'China',
    'sweden': 'Sweden',
    'ch': 'Switzerland',
    'ru': 'Russia',
    'singapore': 'Singapore',
    'iran': 'Iran',
    'colombia': 'Colombia',
    'serbia': 'Serbia',
    'japan': 'Japan',
    'israel': 'Israel',
    'mexico': 'Mexico', 'mx': 'Mexico',
    'ethiopia': 'Ethiopia',
    'af': 'South Africa',   # in context: African institution
    'africa': 'South Africa',  # default Africa → South Africa (SAAO context)
    'georgia': 'Georgia',
}

def email_to_country(email):
    """Guess country from email domain TLD."""
    if not email or '@' not in email:
        return None
    domain = email.split('@')[-1].lower().strip()
    # strip mailto: prefix if present
    domain = domain.replace('mailto:', '')
    parts = domain.split('.')
    # Check .ac.uk
    if domain.endswith('.ac.uk') or domain.endswith('.roe.ac.uk'):
        return 'United Kingdom'
    # Check 2-letter ccTLD at end
    if len(parts) >= 2:
        tld = parts[-1]
        if tld in TLD_TO_COUNTRY:
            return TLD_TO_COUNTRY[tld]
        # Check second-to-last for country (e.g. .ac.za, .edu.au)
        if len(parts) >= 3 and parts[-2] in ('ac', 'edu', 'gov', 'org', 'co', 'com'):
            tld2 = parts[-1]
            if tld2 in TLD_TO_COUNTRY:
                return TLD_TO_COUNTRY[tld2]
    return None

def resolve_country(cc_raw, email):
    """Return a country name from the continent/country field + email."""
    cc = cc_raw.strip().lower().rstrip('.')
    # Direct map
    if cc in CC_MAP:
        return CC_MAP[cc]
    # EU / European: try email TLD
    if cc in ('eu', 'europe', 'eu, georgia'):
        c = email_to_country(email)
        if c:
            return c
        if 'georgia' in cc:
            return 'Georgia'
        return 'Europe (unspecified)'
    # US/NZ dual
    if 'us/nz' in cc or 'us / nz' in cc:
        return 'United States'
    if 'canada (previously' in cc:
        return 'Canada'
    # Fall back to email
    c = email_to_country(email)
    if c:
        return c
    return None


def get_members_csv_url():
    """Return the CSV URL for the members data without hard-coding it.

    Resolution order:
    1) Environment variable: TVS_MEMBERS_CSV_URL
    2) Local config file (untracked): tvs_map_names_config.json
         - {"members_csv_url": "https://<private-csv-url>"}
    """

    csv_url = (os.getenv('TVS_MEMBERS_CSV_URL') or '').strip()
    if csv_url:
        return csv_url

    cfg_path = Path(__file__).resolve().parent / 'tvs_map_names_config.json'
    if cfg_path.exists():
        cfg = json.loads(cfg_path.read_text(encoding='utf-8'))
        cfg_csv_url = str(cfg.get('members_csv_url', '')).strip()
        if cfg_csv_url:
            return cfg_csv_url

    raise SystemExit(
        'Missing members CSV URL configuration. Set TVS_MEMBERS_CSV_URL or create tvs_map_names_config.json '
        'with a "members_csv_url" value.'
    )


# --- Load spreadsheet directly from Google Sheets ---
CSV_URL = get_members_csv_url()

print('Fetching members CSV data...')
df_raw = pd.read_csv(CSV_URL, dtype=str).fillna('')

# Find columns by name (case-insensitive)
cols = {c.strip().lower(): c for c in df_raw.columns}
surname_col = cols.get('surname', df_raw.columns[0])
cc_col      = cols.get('continent/country', df_raw.columns[3])
email_col   = cols.get('email', df_raw.columns[4])
print(f"Using columns: surname={surname_col!r}, cc={cc_col!r}, email={email_col!r}")

country_list = []
country_names = {}   # country -> sorted list of "First Surname"
unresolved = []

firstname_col = cols.get('first name', df_raw.columns[1])

for _, row in df_raw.iterrows():
    s  = str(row[surname_col]).strip()
    if not s:
        continue
    f  = str(row[firstname_col]).strip()
    cc = str(row[cc_col]).strip()
    e1 = str(row[email_col]).strip()
    country = resolve_country(cc, e1)
    if country:
        country_list.append(country)
        full_name = f'{f} {s}' if f else s
        country_names.setdefault(country, []).append(full_name)
    else:
        unresolved.append((s, cc, e1))

# Sort names alphabetically within each country
for c in country_names:
    country_names[c].sort()

counts = Counter(country_list)
print(f"Resolved: {len(country_list)}, Unresolved: {len(unresolved)}")
print("\nCounts:")
for c, n in counts.most_common():
    print(f"  {n:3d}  {c}")
if unresolved:
    print("\nUnresolved:")
    for r in unresolved:
        print(" ", r)

# --- Build dataframe ---
df = pd.DataFrame(counts.items(), columns=['country', 'members'])
df = df.sort_values('members', ascending=False)

# Add name list as a column (newline-separated for tooltip)
# For large countries, show first 30 names + "… and N more"
MAX_NAMES = 30
def format_names(country):
    names = country_names.get(country, [])
    if len(names) <= MAX_NAMES:
        return '<br>'.join(names)
    shown = names[:MAX_NAMES]
    remaining = len(names) - MAX_NAMES
    return '<br>'.join(shown) + f'<br><i>… and {remaining} more</i>'

df['name_list'] = df['country'].apply(format_names)

# --- Log-scale colour mapping ---
df['log_members'] = np.log10(df['members'])

# Build custom tickvals/ticktext for the colorbar (powers of 10 + intermediates)
max_val = df['members'].max()
tickvals = []
ticktext = []
for exp in range(0, math.ceil(math.log10(max_val)) + 1):
    for mult in [1, 2, 5]:
        v = mult * 10**exp
        if 1 <= v <= max_val:
            tickvals.append(math.log10(v))
            ticktext.append(str(v))

# --- Plotly choropleth ---
fig = px.choropleth(
    df,
    locations='country',
    locationmode='country names',
    color='log_members',
    color_continuous_scale='Blues',
    title='LSST TVS Collaboration — Members by Country',
    hover_name='country',
    hover_data={'members': True, 'log_members': False, 'name_list': False},
    custom_data=['members'],
    range_color=(0, math.log10(max_val)),
)
fig.update_traces(
    hovertemplate=(
        '<b>%{hovertext}</b><br>'
        'Members: %{customdata[0]}'
        '<extra></extra>'
    )
)
fig.update_layout(
    title_font_size=18,
    geo=dict(
        showframe=False,
        showcoastlines=True,
        projection_type='natural earth',
        bgcolor='#e8edf2',
        landcolor='#d4dce6',
        oceancolor='#e8edf2',
        showocean=True,
    ),
    coloraxis_colorbar=dict(
        title='Members',
        thickness=16,
        len=0.65,
        tickvals=tickvals,
        ticktext=ticktext,
        tickfont=dict(size=12),
    ),
    margin=dict(l=0, r=0, t=50, b=0),
    paper_bgcolor='white',
)

import json

# Store full (unsplit) name lists for the JS side panel
all_names_json = json.dumps({c: country_names[c] for c in country_names})

# Render figure to HTML string, then inject side panel + JS
html_str = fig.to_html(full_html=True, include_plotlyjs='cdn')

INJECT = f"""
<style>
  #side-panel {{
    position: fixed;
    top: 60px;
    right: 20px;
    width: 240px;
    max-height: 75vh;
    background: rgba(255,255,255,0.96);
    border: 1px solid #aac4e0;
    border-radius: 8px;
    box-shadow: 2px 4px 12px rgba(0,0,0,0.18);
    font-family: Arial, sans-serif;
    font-size: 13px;
    display: none;
    flex-direction: column;
    z-index: 1000;
  }}
  #panel-header {{
    padding: 10px 14px 6px;
    background: #1a6eb5;
    color: white;
    border-radius: 7px 7px 0 0;
    flex-shrink: 0;
  }}
  #panel-header .country-name {{
    font-size: 15px;
    font-weight: bold;
  }}
  #panel-header .member-count {{
    font-size: 12px;
    opacity: 0.85;
    margin-top: 2px;
  }}
  #panel-body {{
    overflow-y: auto;
    padding: 8px 14px 10px;
    flex-grow: 1;
    line-height: 1.6;
    color: #222;
  }}
  #panel-body div {{
    border-bottom: 1px solid #eef2f7;
    padding: 1px 0;
  }}
  #panel-body div:last-child {{ border-bottom: none; }}
</style>

<div id="side-panel">
  <div id="panel-header">
    <div class="country-name" id="panel-country"></div>
    <div class="member-count" id="panel-count"></div>
  </div>
  <div id="panel-body" id="panel-names"></div>
</div>

<script>
const allNames = {all_names_json};
let hideTimer = null;

const gd = document.querySelector('.plotly-graph-div');
const panel = document.getElementById('side-panel');

function showPanel(country) {{
  clearTimeout(hideTimer);
  const names = allNames[country];
  if (!names) return;
  document.getElementById('panel-country').textContent = country;
  document.getElementById('panel-count').textContent = names.length + ' member' + (names.length !== 1 ? 's' : '');
  const body = document.getElementById('panel-body');
  body.innerHTML = names.map(n => '<div>' + n + '</div>').join('');
  panel.style.display = 'flex';
}}

function scheduleHide() {{
  hideTimer = setTimeout(function() {{
    panel.style.display = 'none';
  }}, 300);
}}

gd.on('plotly_hover', function(data) {{
  const pt = data.points[0];
  showPanel(pt.hovertext || pt.location);
}});

gd.on('plotly_unhover', function() {{
  scheduleHide();
}});

// Keep panel open while mouse is over it
panel.addEventListener('mouseenter', function() {{
  clearTimeout(hideTimer);
}});

panel.addEventListener('mouseleave', function() {{
  scheduleHide();
}});
</script>
"""

# Inject before </body>
html_str = html_str.replace('</body>', INJECT + '\n</body>')

out = Path(__file__).resolve().parent / 'tvs_world_map_names.html'
out.write_text(html_str, encoding='utf-8')
print(f"\nSaved: {out}")

# Also save static PNG
out_png = Path(__file__).resolve().parent / 'tvs_world_map_names.png'
fig.write_image(str(out_png), width=1600, height=900, scale=2)
print(f"Saved: {out_png}")
