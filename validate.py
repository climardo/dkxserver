import re
from requests import Session

def valid_contest_id(contest_id):
    valid_id = re.search('^\d{9,}$', contest_id)
    id_from_url = re.search('(draftkings\.com.*contest.*)(\d{9,})', contest_id, re.IGNORECASE)
    
    if id_from_url:
        contest_id = id_from_url.group(2)
    elif valid_id:
        contest_id = contest_id
    else:
        return False

    return contest_id
    
def get_missing_lineup(contest_id, all_members):
    missing_lineup = []
    s = Session()
    contest_details = s.get(f'https://www.draftkings.com/contest/detailspop?contestId={contest_id}')
    for member in all_members:
        if member not in contest_details.text:
            missing_lineup.append(member)
    return missing_lineup
