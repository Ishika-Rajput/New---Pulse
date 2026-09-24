from dateutil import parser


def parse_date(value: str):
    return parser.parse(value) if value else None
