"""
Long winded constants and such live here. Most notably the LANGS tuple.
Unlike in the php version no sql is necessary to add a new language. You only
need to append a new tuple and restart the server. This is equally true
for other constants that appear here.
"""

from markdown import markdown
from .utils import rest
from postmarkup import render_bbcode


LANGS = (
    ("afr", "Afrikaans"),
    ("ain", "Ainu"),
    ("sqi", "Albanian"),
    ("arq", "Algerian Arabic"),
    ("grc", "Ancient Greek"),
    ("ara", "Arabic"),
    ("hye", "Armenian"),
    ("ast", "Asturian"),
    ("aze", "Azerbaijani"),
    ("eus", "Basque"),
    ("bel", "Belarusian"),
    ("ben", "Bengali"),
    ("ber", "Berber"),
    ("bos", "Bosnian"),
    ("bre", "Breton"),
    ("bul", "Bulgarian"),
    ("yue", "Cantonese"),
    ("cat", "Catalan"),
    ("cha", "Chamorro"),
    ("cmn", "Chinese"),
    ("ckt", "Chukchi"),
    ("cor", "Cornish"),
    ("hrv", "Croatian"),
    ("cycl", "CycL"),
    ("ces", "Czech"),
    ("dan", "Danish"),
    ("nld", "Dutch"),
    ("arz", "Egyptian Arabic"),
    ("eng", "English"),
    ("epo", "Esperanto"),
    ("est", "Estonian"),
    ("ewe", "Ewe"),
    ("fao", "Faroese"),
    ("fin", "Finnish"),
    ("fra", "French"),
    ("fry", "Frisian"),
    ("glg", "Galician"),
    ("kat", "Georgian"),
    ("deu", "German"),
    ("grn", "Guarani"),
    ("heb", "Hebrew"),
    ("hil", "Hiligaynon"),
    ("hin", "Hindi"),
    ("hun", "Hungarian"),
    ("isl", "Icelandic"),
    ("ido", "Ido"),
    ("ind", "Indonesian"),
    ("ina", "Interlingua"),
    ("ile", "Interlingue"),
    ("acm", "Iraqi Arabic"),
    ("gle", "Irish"),
    ("ita", "Italian"),
    ("jpn", "Japanese"),
    ("xal", "Kalmyk"),
    ("kaz", "Kazakh"),
    ("khm", "Khmer"),
    ("tlh", "Klingon"),
    ("kor", "Korean"),
    ("avk", "Kotava"),
    ("kur", "Kurdish"),
    ("ksh", "Kolsch"),
    ("lld", "Ladin"),
    ("lad", "Ladino"),
    ("lao", "Lao"),
    ("lat", "Latin"),
    ("lvs", "Latvian"),
    ("lzh", "Literary Chinese"),
    ("lit", "Lithuanian"),
    ("jbo", "Lojban"),
    ("dsb", "Lower Sorbian"),
    ("nds", "Low Saxon"),
    ("mlg", "Malagasy"),
    ("zsm", "Malay"),
    ("mal", "Malayalam"),
    ("mlt", "Maltese"),
    ("mri", "Maori"),
    ("mar", "Marathi"),
    ("ell", "Modern Greek"),
    ("mon", "Mongolian"),
    ("npi", "Nepali"),
    ("nob", "Norwegian (Bokmal)"),
    ("non", "Norwegian (Nynorsk)"),
    ("nov", "Novial"),
    ("oci", "Occitan"),
    ("orv", "Old East Slavic"),
    ("ang", "Old English"),
    ("prg", "Old Prussian"),
    ("tpw", "Old Tupi"),
    ("oss", "Ossetian"),
    ("pes", "Persian"),
    ("pcd", "Picard"),
    ("pms", "Piemontese"),
    ("pol", "Polish"),
    ("por", "Portuguese"),
    ("pnb", "Punjabi"),
    ("que", "Quechua"),
    ("qya", "Quenya"),
    ("ron", "Romanian"),
    ("roh", "Romansh"),
    ("rus", "Russian"),
    ("san", "Sanskrit"),
    ("gla", "Scottish Gaelic"),
    ("srp", "Serbian"),
    ("wuu", "Shanghainese"),
    ("scn", "Sicilian"),
    ("sjn", "Sindarin"),
    ("slk", "Slovak"),
    ("slv", "Slovenian"),
    ("spa", "Spanish"),
    ("bod", "Standard Tibetan"),
    ("swh", "Swahili"),
    ("swe", "Swedish"),
    ("tgl", "Tagalog"),
    ("tgk", "Tajik"),
    ("tat", "Tatar"),
    ("tel", "Telugu"),
    ("nan", "Teochew"),
    ("tha", "Thai"),
    ("toki", "Toki Pona"),
    ("tpi", "Tok Pisin"),
    ("tur", "Turkish"),
    ("ukr", "Ukrainian"),
    ("hsb", "Upper Sorbian"),
    ("urd", "Urdu"),
    ("uig", "Uyghur"),
    ("uzb", "Uzbek"),
    ("vie", "Vietnamese"),
    ("vol", "Volapuk"),
    ("cym", "Welsh"),
    ("xho", "Xhosa"),
    ("yid", "Yiddish"),
)

# use Log.get_type_display() to get the readable part
# for display in templates
LOG_ACTIONS = (
    ('sad', 'Sentence added'),
    ('sed', 'Sentence edited'),
    ('srd', 'Sentence removed'),
    ('sld', 'Sentence locked'),
    ('sul', 'Sentence unlocked'),
    ('soa', 'Sentence adopted'),
    ('sor', 'Sentence released'),
    ('slc', 'Sentence language changed'),
    ('lad', 'Link added'),
    ('lrd', 'Link removed'),
    ('cma', 'Comment added'),
    ('cme', 'Comment edited'),
    ('cmr', 'Comment removed'),
    ('tad', 'Tag added'),
    ('trd', 'Tag removed'),
    ('usd', 'User subscribed'),
    ('uud', 'User unsubscribed'),
    ('cad', 'Correction added'),
    ('ced', 'Correction edited'),
    ('crd', 'Correction removed'),
    ('crj', 'Correction rejected'),
    ('cac', 'Correction accepted'),
    ('cfd', 'Correction forced'),
)

PRIVACY = (
    ('o', 'Open'),
    ('r', 'Registered'),
)

USER_STATUS = (
    ('a', 'Admin'),
    ('m', 'Moderator'),
    ('t', 'Trusted User'),
    ('u', 'Normal User'),
)

PROFICIENCY = (
    ('n', 'Native'),
    ('f', 'Fluent'),
    ('a', 'Advanced'),
    ('i', 'Intermediate'),
    ('b', 'Beginner'),
)

VOTE_ON = (
    ('lp', 'Language Proficiency'),
    ('sp', 'Status Promotion'),
)

MARKUPS_SUPPORTED = {
    'md': ('Markdown', markdown),
    'rs': ('reStructuredText', rest),
    'bb': ('BBCode', render_bbcode),
}

MARKUPS = tuple((k, v[0]) for k, v in MARKUPS_SUPPORTED.iteritems())

# iso 3166 country codes
COUNTRIES = (
    ('AD', 'Andorra'),
    ('AE', 'United Arab Emirates'),
    ('AF', 'Afghanistan'),
    ('AG', 'Antigua and Barbuda'),
    ('AI', 'Anguilla'),
    ('AL', 'Albania'),
    ('AM', 'Armenia'),
    ('AO', 'Angola'),
    ('AR', 'Argentina'),
    ('AS', 'American Samoa'),
    ('AT', 'Austria'),
    ('AU', 'Australia'),
    ('AW', 'Aruba'),
    ('AX', 'Aland Islands'),
    ('AZ', 'Azerbaijan'),
    ('BA', 'Bosnia and Herzegovina'),
    ('BB', 'Barbados'),
    ('BD', 'Bangladesh'),
    ('BE', 'Belgium'),
    ('BF', 'Burkina Faso'),
    ('BG', 'Bulgaria'),
    ('BH', 'Bahrain'),
    ('BI', 'Burundi'),
    ('BJ', 'Benin'),
    ('BL', 'Saint Bartelemey'),
    ('BM', 'Bermuda'),
    ('BN', 'Brunei Darussalam'),
    ('BO', 'Bolivia'),
    ('BQ', 'Bonaire, Saint Eustatius and Saba'),
    ('BR', 'Brazil'),
    ('BS', 'Bahamas'),
    ('BT', 'Bhutan'),
    ('BV', 'Bouvet Island'),
    ('BW', 'Botswana'),
    ('BY', 'Belarus'),
    ('BZ', 'Belize'),
    ('CA', 'Canada'),
    ('CC', 'Cocos (Keeling) Islands'),
    ('CD', 'Congo, The Democratic Republic of the'),
    ('CF', 'Central African Republic'),
    ('CG', 'Congo'),
    ('CH', 'Switzerland'),
    ('CI', 'Cote d\'Ivoire'),
    ('CK', 'Cook Islands'),
    ('CL', 'Chile'),
    ('CM', 'Cameroon'),
    ('CN', 'China'),
    ('CO', 'Colombia'),
    ('CR', 'Costa Rica'),
    ('CU', 'Cuba'),
    ('CV', 'Cape Verde'),
    ('CW', 'Curacao'),
    ('CX', 'Christmas Island'),
    ('CY', 'Cyprus'),
    ('CZ', 'Czech Republic'),
    ('DE', 'Germany'),
    ('DJ', 'Djibouti'),
    ('DK', 'Denmark'),
    ('DM', 'Dominica'),
    ('DO', 'Dominican Republic'),
    ('DZ', 'Algeria'),
    ('EC', 'Ecuador'),
    ('EE', 'Estonia'),
    ('EG', 'Egypt'),
    ('EH', 'Western Sahara'),
    ('ER', 'Eritrea'),
    ('ES', 'Spain'),
    ('ET', 'Ethiopia'),
    ('FI', 'Finland'),
    ('FJ', 'Fiji'),
    ('FK', 'Falkland Islands (Malvinas)'),
    ('FM', 'Micronesia, Federated States of'),
    ('FO', 'Faroe Islands'),
    ('FR', 'France'),
    ('GA', 'Gabon'),
    ('GB', 'United Kingdom'),
    ('GD', 'Grenada'),
    ('GE', 'Georgia'),
    ('GF', 'French Guiana'),
    ('GG', 'Guernsey'),
    ('GH', 'Ghana'),
    ('GI', 'Gibraltar'),
    ('GL', 'Greenland'),
    ('GM', 'Gambia'),
    ('GN', 'Guinea'),
    ('GP', 'Guadeloupe'),
    ('GQ', 'Equatorial Guinea'),
    ('GR', 'Greece'),
    ('GS', 'South Georgia and the South Sandwich Islands'),
    ('GT', 'Guatemala'),
    ('GU', 'Guam'),
    ('GW', 'Guinea-Bissau'),
    ('GY', 'Guyana'),
    ('HK', 'Hong Kong'),
    ('HM', 'Heard Island and McDonald Islands'),
    ('HN', 'Honduras'),
    ('HR', 'Croatia'),
    ('HT', 'Haiti'),
    ('HU', 'Hungary'),
    ('ID', 'Indonesia'),
    ('IE', 'Ireland'),
    ('IL', 'Israel'),
    ('IM', 'Isle of Man'),
    ('IN', 'India'),
    ('IO', 'British Indian Ocean Territory'),
    ('IQ', 'Iraq'),
    ('IR', 'Iran, Islamic Republic of'),
    ('IS', 'Iceland'),
    ('IT', 'Italy'),
    ('JE', 'Jersey'),
    ('JM', 'Jamaica'),
    ('JO', 'Jordan'),
    ('JP', 'Japan'),
    ('KE', 'Kenya'),
    ('KG', 'Kyrgyzstan'),
    ('KH', 'Cambodia'),
    ('KI', 'Kiribati'),
    ('KM', 'Comoros'),
    ('KN', 'Saint Kitts and Nevis'),
    ('KP', 'Korea, Democratic People\'s Republic of'),
    ('KR', 'Korea, Republic of'),
    ('KW', 'Kuwait'),
    ('KY', 'Cayman Islands'),
    ('KZ', 'Kazakhstan'),
    ('LA', 'Lao People\'s Democratic Republic'),
    ('LB', 'Lebanon'),
    ('LC', 'Saint Lucia'),
    ('LI', 'Liechtenstein'),
    ('LK', 'Sri Lanka'),
    ('LR', 'Liberia'),
    ('LS', 'Lesotho'),
    ('LT', 'Lithuania'),
    ('LU', 'Luxembourg'),
    ('LV', 'Latvia'),
    ('LY', 'Libyan Arab Jamahiriya'),
    ('MA', 'Morocco'),
    ('MC', 'Monaco'),
    ('MD', 'Moldova, Republic of'),
    ('ME', 'Montenegro'),
    ('MF', 'Saint Martin'),
    ('MG', 'Madagascar'),
    ('MH', 'Marshall Islands'),
    ('MK', 'Macedonia'),
    ('ML', 'Mali'),
    ('MM', 'Myanmar'),
    ('MN', 'Mongolia'),
    ('MO', 'Macao'),
    ('MP', 'Northern Mariana Islands'),
    ('MQ', 'Martinique'),
    ('MR', 'Mauritania'),
    ('MS', 'Montserrat'),
    ('MT', 'Malta'),
    ('MU', 'Mauritius'),
    ('MV', 'Maldives'),
    ('MW', 'Malawi'),
    ('MX', 'Mexico'),
    ('MY', 'Malaysia'),
    ('MZ', 'Mozambique'),
    ('NA', 'Namibia'),
    ('NC', 'New Caledonia'),
    ('NE', 'Niger'),
    ('NF', 'Norfolk Island'),
    ('NG', 'Nigeria'),
    ('NI', 'Nicaragua'),
    ('NL', 'Netherlands'),
    ('NO', 'Norway'),
    ('NP', 'Nepal'),
    ('NR', 'Nauru'),
    ('NU', 'Niue'),
    ('NZ', 'New Zealand'),
    ('OM', 'Oman'),
    ('PA', 'Panama'),
    ('PE', 'Peru'),
    ('PF', 'French Polynesia'),
    ('PG', 'Papua New Guinea'),
    ('PH', 'Philippines'),
    ('PK', 'Pakistan'),
    ('PL', 'Poland'),
    ('PM', 'Saint Pierre and Miquelon'),
    ('PN', 'Pitcairn'),
    ('PR', 'Puerto Rico'),
    ('PS', 'Palestinian Territory'),
    ('PT', 'Portugal'),
    ('PW', 'Palau'),
    ('PY', 'Paraguay'),
    ('QA', 'Qatar'),
    ('RE', 'Reunion'),
    ('RO', 'Romania'),
    ('RS', 'Serbia'),
    ('RU', 'Russian Federation'),
    ('RW', 'Rwanda'),
    ('SA', 'Saudi Arabia'),
    ('SB', 'Solomon Islands'),
    ('SC', 'Seychelles'),
    ('SD', 'Sudan'),
    ('SE', 'Sweden'),
    ('SG', 'Singapore'),
    ('SH', 'Saint Helena'),
    ('SI', 'Slovenia'),
    ('SJ', 'Svalbard and Jan Mayen'),
    ('SK', 'Slovakia'),
    ('SL', 'Sierra Leone'),
    ('SM', 'San Marino'),
    ('SN', 'Senegal'),
    ('SO', 'Somalia'),
    ('SR', 'Suriname'),
    ('SS', 'South Sudan'),
    ('ST', 'Sao Tome and Principe'),
    ('SV', 'El Salvador'),
    ('SX', 'Sint Maarten'),
    ('SY', 'Syrian Arab Republic'),
    ('SZ', 'Swaziland'),
    ('TC', 'Turks and Caicos Islands'),
    ('TD', 'Chad'),
    ('TF', 'French Southern Territories'),
    ('TG', 'Togo'),
    ('TH', 'Thailand'),
    ('TJ', 'Tajikistan'),
    ('TK', 'Tokelau'),
    ('TL', 'Timor-Leste'),
    ('TM', 'Turkmenistan'),
    ('TN', 'Tunisia'),
    ('TO', 'Tonga'),
    ('TR', 'Turkey'),
    ('TT', 'Trinidad and Tobago'),
    ('TV', 'Tuvalu'),
    ('TW', 'Taiwan'),
    ('TZ', 'Tanzania, United Republic of'),
    ('UA', 'Ukraine'),
    ('UG', 'Uganda'),
    ('UM', 'United States Minor Outlying Islands'),
    ('US', 'United States'),
    ('UY', 'Uruguay'),
    ('UZ', 'Uzbekistan'),
    ('VA', 'Holy See (Vatican City State)'),
    ('VC', 'Saint Vincent and the Grenadines'),
    ('VE', 'Venezuela'),
    ('VG', 'Virgin Islands, British'),
    ('VI', 'Virgin Islands, U.S.'),
    ('VN', 'Vietnam'),
    ('VU', 'Vanuatu'),
    ('WF', 'Wallis and Futuna'),
    ('WS', 'Samoa'),
    ('YE', 'Yemen'),
    ('YT', 'Mayotte'),
    ('ZA', 'South Africa'),
    ('ZM', 'Zambia'),
    ('ZW', 'Zimbabwe'),
)
