#!/usr/bin/python3
#
# Scrapper is a tool to download ejudge run archives and extract them
# to a local filesystem.
#

from bs4 import BeautifulSoup
from requests import post, get
from getpass import getpass
from urllib.parse import urlparse, parse_qsl


BASE_URL = "https://apathism.net/cgi-bin/new-master"
EJUDGE_RUN_FILTER = "status == OK && latest && login != \"ejudge\""

def make_range(a, b = None):
    if b is None:
        return (a,)
    return range(a, b + 1)

def parse_contests_list(input):
    numbers = set()
    for interval in input.split(','):
        values = interval.split('-')
        if 1 <= len(values) <= 2:
            numbers = numbers.union(set(make_range(*map(int, values))))
        else:
            raise ValueError('Invalid number of boundaries in inverval')
    return list(numbers)

def download_contest(contest_id, page):
    SID = list(e for e in BeautifulSoup(page.text, 'html.parser').find_all('input')
               if e.get('name') == 'SID')[0].get('value')
    filtered_page = post(BASE_URL, data={
        'SID': SID,
        'filter_expr': EJUDGE_RUN_FILTER,
        'filter_first_run': '',
        'filter_last_run': '0',
        'filter_view_1': 'View',
    }, cookies=page.cookies)
    filtered_page.raise_for_status()
    bs = BeautifulSoup(filtered_page.text, 'html.parser')
    inputs = bs.find_all('input')
    run_mask_size = list(e for e in inputs if e.get('name') == 'run_mask_size')[0].get('value')
    run_mask = list(e for e in inputs if e.get('name') == 'run_mask')[0].get('value')
    print('Runs: {}'.format(list(e.get_text() for e in bs.find_all("big") if e.get_text().startswith('Total'))[0]))
    download_page = post(BASE_URL, data={
        'SID': SID,
        'run_mask_size': run_mask_size,
        'run_mask': run_mask,
        'run_selection': 1,
        'file_pattern_contest': 'on',
        'file_pattern_run': 'on',
        'file_pattern_login': 'on',
        'file_pattern_prob': 'on',
        'file_pattern_time': 'on',
        'file_pattern_suffix': 'on',
        'dir_struct': 0,
        'use_problem_dir': 'on',
        'action_149': '1',
    }, cookies=filtered_page.cookies)
    download_page.raise_for_status()
    with open('archives/{}.tgz'.format(contest_id), 'wb') as f:
        f.write(download_page.content)

ejudge_login = input('Ejudge login: ')
ejudge_password = getpass('Ejudge password: ')
contests = parse_contests_list(input('Contests: '))

print()
print('Everything is initiated, and ready to go...')

for contest in contests:
    print()
    print('Downloading contest {}... '.format(contest))
    master_page = post(BASE_URL, data={
        'login': ejudge_login,
        'password': ejudge_password,
        'contest_id': contest,
        'role': 6,
        'locale_id': 0,
    })
    master_page.raise_for_status()
    download_contest(contest, master_page)
