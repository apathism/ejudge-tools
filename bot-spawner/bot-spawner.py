import sys

print('''
<?xml version="1.0" encoding="UTF-8" ?>
<runlog contest_id="6801" duration="18000" start_time="2018/10/20 00:00:00" current_time="2018/10/21 15:38:23" fog_time="3600">
  <runs>
''')

runs = []
for i, line in enumerate(sys.stdin.readlines()):
    items = [x.split('<br>') for x in line.rstrip().split('<td>')[2:]]
    user_id = 2001 + i
    runs.append((0, 0, user_id, None, "VS"))
    runs.append((5 * 60 * 60, 0, user_id, None, "VT"))
    for task, e in enumerate(items):
        time = 0
        if len(e) >= 2:
            [m, s] = map(int, e[1].split(':'))
            time = (m * 60 + s)
        if e[0][0] == '+':
            mistakes = int('0' + e[0][1:])
            for mistake in range(mistakes):
                runs.append((time, mistake, user_id, task + 1, "WA"))
            runs.append((time, mistakes, user_id, task + 1, "OK"))

runs = list(sorted(runs))
for id, (sec, nsec, user_id, task_id, status) in enumerate(runs):
    print('<run', end='')
    print(' run_id="{}"'.format(id), end='')
    print(' time="{}"'.format(sec), end='')
    print(' nsec="{}"'.format(nsec), end='')
    print(' user_id="{}"'.format(user_id), end='')
    #if task_id is not None:
    print(' prob_id="{}"'.format(task_id if task_id is not None else 1), end='')
    print(' status="{}"'.format(status), end='')
    print(' lang_id="3"', end='')
    print('/>')    

print('''</runs>
</runlog>
''')
