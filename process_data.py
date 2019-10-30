import csv
import json
import itertools

PARTIES = ['conservative', 'liberal', 'ndp', 'green', 'bloc']

BASE_URL = 'https://www.ourcommons.ca/Parliamentarians/en/votes/%d/%d/%d/'

if __name__ == '__main__':
	headers = ['Date', 'Parliament Number', 'Session Number', 'Decision Number', 
	'Result', 'Decision Type', 'Decision Subject', 'Num Yeas', 'Num Nays', 'Num Paired',
	'Conservative Yeas', 'Conservative Nays', 'Liberal Yeas', 'Liberal Nays',
	'NDP Yeas', 'NDP Nays', 'Green Yeas', 'Green Nays', 'Bloc Yeas', 'Bloc Nays', 'URL']

	for party in PARTIES:
		headers.append(party.capitalize() + ' Defections')
	for two_party_coalitions in itertools.combinations(PARTIES, 2):
		headers.append('%s-%s Coalition' % 
			(two_party_coalitions[0].capitalize(), two_party_coalitions[1].capitalize()))
	for three_party_coalitions in itertools.combinations(PARTIES, 3):
		headers.append('%s-%s-%s Coalition' % 
			(three_party_coalitions[0].capitalize(), three_party_coalitions[1].capitalize(), 
				three_party_coalitions[2].capitalize()))
	csv_output = []	
	with open("voting_records.json") as f:
		for entry in json.load(f):
			csv_row = [entry['date'], entry['parliament_number'], entry['session_number'], 
			entry['decision_number'], entry['result'], entry['decision_type'], entry['decision_subject'],
			entry['num_yeas'], entry['num_nays'], entry['num_paired'], 
			entry['conservative_yeas'], entry['conservative_nays'], entry['liberal_yeas'], entry['liberal_nays'], 
			entry['ndp_yeas'], entry['ndp_nays'], entry['green_yeas'], 
			entry['green_nays'], entry['bloc_yeas'], entry['bloc_nays']]

			csv_row.append(BASE_URL % (entry['parliament_number'],entry['session_number'],entry['decision_number']))
			# Defections
			for party in PARTIES:
				if entry[party+'_yeas'] > 0 and entry[party+'_nays'] > 0:
					csv_row.append('1')
				else:
					csv_row.append('0')
			# 2 party coalitions
			for two_party_coalitions in itertools.combinations(PARTIES, 2):
				if (entry[two_party_coalitions[0]+'_yeas'] > entry[two_party_coalitions[0]+'_nays'] and 
					entry[two_party_coalitions[1]+'_yeas'] > entry[two_party_coalitions[1]+'_nays']):
					csv_row.append('1')
				else:
					csv_row.append('0')
			# 3 party coalitions
			for three_party_coalitions in itertools.combinations(PARTIES, 3):
				if (entry[three_party_coalitions[0]+'_yeas'] > entry[three_party_coalitions[0]+'_nays'] and 
					entry[three_party_coalitions[1]+'_yeas'] > entry[three_party_coalitions[1]+'_nays'] and 
					entry[three_party_coalitions[2]+'_yeas'] > entry[three_party_coalitions[2]+'_nays']):
					csv_row.append('1')
				else:
					csv_row.append('0')

			csv_output.append([str(data) for data in csv_row])
	## Sort by date
	csv_output.sort(key=lambda x: x[0])
	csv_output.insert(0, headers)
	with open("processed_data.csv", "w") as outfile:
		writer = csv.writer(outfile)
		writer.writerows(csv_output)
