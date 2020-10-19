import re
from flask import flash, redirect, url_for

def valid_contest_id(contest_id):
    valid_id = re.search('^\d{8,}$', contest_id)
    id_from_url = re.search('(draftkings\.com.*contest.*)(\d{8,})', contest_id, re.IGNORECASE)
    
    if id_from_url:
        contest_id = id_from_url.group(2)
    elif valid_id:
        contest_id = contest_id
    else:
        return False

    return contest_id
    