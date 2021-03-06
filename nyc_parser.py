import argparse
import csv
import sys

arg_parser = argparse.ArgumentParser(description='Parse nyc voting csv\'s.')
arg_parser.add_argument('csvfilepath', type=str, nargs=1)
arg_parser.add_argument('--print_header', type=bool, default=False)

args = arg_parser.parse_args()

precinct_to_data = {}

other_vote_titles = ['Public Counter', 'Emergency', 'Absentee/Military', 'Federal', 'Affidavit', 'Scattered']

office_mapping = {
  'Representative in Congress': 'U.S. House',
  'State Senator': 'State Senate',
  'Member of the Assembly': 'State Assembly'
}

if args.print_header:
    print('county,precinct,office,district,party,candidate,votes,public_counter_votes,emergency_votes,absentee_military_votes,federal_votes,affidavit_votes')
with open(args.csvfilepath[0], 'rb') as csvfile:
  line = csv.reader(csvfile, delimiter=',', quotechar='"')
  line_number = 0
  for row in line:
    if line_number == 0:
      line_number += 1
      continue
    (ad, ed, county, edad_status, _, party, office, district, _, candidate, votes) = row
    precinct = '%s/%s' % (ed, ad)
    data = precinct_to_data.get(precinct, {})
    data[candidate] = {}
    data[candidate]['county'] = county
    data[candidate]['party'] = party
    data[candidate]['office'] = office
    data[candidate]['district'] = district
    data[candidate]['votes'] = votes
    data[candidate]['status'] = edad_status
    precinct_to_data[precinct] = data
    line_number += 1

def print_precinct(precinct, data):
  actual_candidates = set(data.keys()) - set(other_vote_titles)
  for candidate in actual_candidates:
    candidate_data = data.get(candidate)
    votes = 0
    if candidate_data:
      votes = int(candidate_data['votes'])
    line = None
    for other_vote_title in other_vote_titles:
      other_vote_data = data.get(other_vote_title)
      if other_vote_data:
        if not line:
          county = other_vote_data['county']
          party = other_vote_data['party']
          office = other_vote_data['office']
          if office in office_mapping:
            office = office_mapping[office];
          district = other_vote_data['district']
          if not district.isdigit():
            district = ''
          else:
            district = int(district)
          line = '%s,%s,%s,%s,%s,%s,%d' % (
            county, precinct, office, district, party, candidate, votes)
        line += ',' + other_vote_data['votes']
    print(line)

for precinct in precinct_to_data:
  data = precinct_to_data[precinct]
  status = data[other_vote_titles[0]]['status']
  if status == 'IN-PLAY':
    print_precinct(precinct, data)

