import os
import requests
import xml.etree.ElementTree as ET
import json
import concurrent.futures

BASE_URL = 'https://www.ourcommons.ca/Parliamentarians/en/HouseVotes/ExportDetailsVotes?output=XML&parliament=%d&session=%d&vote=%d'

## TODO: extract proposingParty
class BillStat(object):
	def __init__(self):
		## Stats coming from the session_xml
		self.proposingParty = ''
		self.date = ''
		self.parliament_number = 0
		self.session_number = 0
		self.decision_number = 0
		self.result = ''
		self.decision_type = ''
		self.decision_subject = ''
		self.num_yeas = 0
		self.num_nays = 0
		self.num_paired = 0

		## Stats coming from the vote_xml
		self.conservative_yeas = 0
		self.conservative_nays = 0
		self.liberal_yeas = 0
		self.liberal_nays = 0
		self.ndp_yeas = 0
		self.ndp_nays = 0
		self.green_yeas = 0
		self.green_nays = 0
		self.bloc_yeas = 0
		self.bloc_nays = 0

def ExtractVoteCounts(vote_xml):
	bill_stat = BillStat()
	for vote_participant in vote_xml:
		party_name = vote_participant.find('PartyName').text.strip().lower()
		vote_value = vote_participant.find('VoteValueName').text.strip().lower()
		if party_name == 'liberal':
			if vote_value == 'nay':
				bill_stat.liberal_nays += 1
			elif vote_value == 'yea':
				bill_stat.liberal_yeas += 1
		elif party_name == 'conservative':
			if vote_value == 'nay':
				bill_stat.conservative_nays += 1
			elif vote_value == 'yea':
				bill_stat.conservative_yeas += 1
		elif party_name == 'ndp':
			if vote_value == 'nay':
				bill_stat.ndp_nays += 1
			elif vote_value == 'yea':
				bill_stat.ndp_yeas += 1
		elif party_name.startswith('bloc qu'): # I don't want to deal with accents
			if vote_value == 'nay':
				bill_stat.bloc_nays += 1
			elif vote_value == 'yea':
				bill_stat.bloc_yeas += 1
		elif party_name == 'green party':
			if vote_value == 'nay':
				bill_stat.green_nays += 1
			elif vote_value == 'yea':
				bill_stat.green_yeas += 1
	return bill_stat

def ParseProposedBill(proposedBill):
	parliament_number = int(proposedBill.find('ParliamentNumber').text)
	session_number = int(proposedBill.find('SessionNumber').text)
	decision_number = int(proposedBill.find('DecisionDivisionNumber').text)
	xml_url = BASE_URL % (parliament_number, session_number, decision_number)
	xml_response = requests.get(xml_url)
	vote_xml = ET.fromstring(xml_response.content)
	bill_stat = ExtractVoteCounts(vote_xml)

	## Set Session XML stats
	bill_stat.proposingParty = ''
	bill_stat.date = proposedBill.find('DecisionEventDateTime').text
	bill_stat.parliament_number = parliament_number
	bill_stat.session_number = session_number
	bill_stat.decision_number = decision_number
	bill_stat.result = proposedBill.find('DecisionResultName').text
	bill_stat.decision_type = proposedBill.find('DecisionDivisionDocumentTypeName').text
	bill_stat.decision_subject = proposedBill.find('DecisionDivisionSubject').text
	bill_stat.num_yeas = proposedBill.find('DecisionDivisionNumberOfYeas').text
	bill_stat.num_nays = proposedBill.find('DecisionDivisionNumberOfNays').text
	bill_stat.num_paired = proposedBill.find('DecisionDivisionNumberOfPaired').text
	return bill_stat


if __name__ == '__main__':
	voting_records = []
	for file_name in os.listdir('./input_data/'):
		if not file_name.startswith('Export') or not file_name.endswith('xml'):
			continue
		print('Parsing file: ' + file_name)
		tree = ET.parse('./input_data/'+file_name)
		root = tree.getroot()
		num_votes = len(root)
		print('The file has %d votes' % num_votes)
		i = 0
		with concurrent.futures.ThreadPoolExecutor(max_workers=num_votes) as executor:
			futures = [executor.submit(ParseProposedBill, proposed_bill) for proposed_bill in root]
			for future in concurrent.futures.as_completed(futures):
				voting_records.append(future.result())
				i+=1
				if i % max(num_votes//10,1) == 0:
					print('Done with %d/%d votes' % (i,num_votes))
		print('Processed %d voting records so far.' % len(voting_records))
	with open('voting_records.json', 'a') as f:
		json.dump(voting_records, f, default= lambda x: x.__dict__)