#import pystache
import sys


class ProblemVerdict:
    verdict = ""
    was = False
    sum = 0

    def __init__(self, scores):
        self.was, self.sum = False, 0
        for x in scores:
            if x is not None:
                self.was = True
                self.sum += x
        if not self.was:
            self.verdict = "<td class='no_submits'>&nbsp;</td>";
        elif self.sum < 100:
            self.verdict = "<td class='not_full'>{}</td>".format(self.sum);
        else:
            self.verdict = "<td class='full'>{}</td>".format(self.sum)

    def __repr__(self):
        return self.verdict


class Result:
    name = ""
    grade = 0
    login = "olymp11-00-00"
    region = ""
    scores = list()
    total_score = 0

    def is_number(self, n):
        try:
            int(n)
            return True
        except ValueError:
            return False

    def parse_scores(self, scores):
        if self.login.startswith('olymp11'):
            new_scores = [[scores[0]], scores[1: -2], [scores[-2]], [scores[-1]]]
        else:
            new_scores = [[scores[0]], [scores[1]], [scores[2]], scores[3:]]
        return list([ProblemVerdict(score) for score in new_scores])

    def nameoficator(self, name):
        return " ".join([word[0].upper() + word[1:] for word in name.split()])

    def __init__(self, line):
        columns = line.strip().split(';')
        self.login = columns[0]
        self.name, self.grade = [x.strip() for x in columns[1].split(',')]
        self.name = self.nameoficator(self.name)
        self.grade = int(self.grade.split()[0])
        self.region = columns[2]
        self.total_score = int(columns[-1])
        self.scores = self.parse_scores([(int(x) if self.is_number(x) else None) for x in columns[3: -1]])
        if (sum([score.sum for score in self.scores if score.was]) != self.total_score):
            print('ACHTUNG: {}'.format(self))

    def get_region(self):
        return int(self.login.split('-')[1])

    def __repr__(self):
        return "<tr><td class='login'>{}</td><td class='name'>{}</td>{}{}<td class='total'>{}</td></tr>".format(
            self.login, self.name,
            ("<td class='grade'>{} класс</td>".format(self.grade) if self.grade else "<td class='grade'><i>?</i></td>"),
            "".join([str(score) for score in self.scores]),
            self.total_score
        )


results = []
for line in open("results.csv"):
    if len(line.strip()):
        results.append(Result(line))

results.sort(key=lambda x: (-x.total_score, x.login))

template = "".join(open("template.html").readlines())

regions = list(set([result.get_region() for result in results]))
for region in regions:
    local_results = list([result for result in results if region == result.get_region()])
    region_name = local_results[0].region.replace('м. р.', 'муниципальный район').replace('г. о.', 'Городской округ')
    code78 = "".join([str(result) for result in local_results if result.login.startswith('olymp08')])
    code911 = "".join([str(result) for result in local_results if result.login.startswith('olymp11')])
    outfile = open("{:02}.html".format(region), "w")
    print(template.replace('##1##', region_name).replace('##2##', code78).replace('##3##', code911), file=outfile)
    outfile.close()
