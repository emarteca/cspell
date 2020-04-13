import pandas as pd 
import xml.etree.ElementTree as ET
import sys

# inspired from stackoverflow: https://stackoverflow.com/questions/28259301/how-to-convert-an-xml-file-to-nice-pandas-dataframe
def parse_xml_file( filename):
	root = ET.parse( filename).getroot()
	# we already know the shape of the tree so we can just hardcode this
	tags = {"tags":[]}
	for ts in root:
		for t in ts:
			tag = {}
			tag["test_id"] = t.attrib["name"] # this is going to be the string we search for matching the desc
			tag["time"] = t.attrib["time"]
			tag["suite_name"] = ts.attrib["name"]
			tag["suite_total_tests"] = ts.attrib["tests"]
			tag["suite_time"] = ts.attrib["time"]
			tags["tags"].append( tag)
	return( pd.DataFrame( tags["tags"]))

def parse_relevant_descs_file( filename):
	to_ret = pd.read_csv( filename, header=None)
	to_ret.columns = ['test_desc']
	return( to_ret)

def append_DF_to_file( df, filename):
	f = open(filename, 'a');
	f.write(df.to_csv(index = False, header=False))
	f.close()

def process_fails_file( filename):
	to_ret = pd.read_csv( filename, sep = ' ', header=None)
	to_ret = to_ret[to_ret[1] == "FAIL"]
	to_ret.drop([1], inplace=True, axis=1) # delete the garbage initial columns
	to_ret.columns = ["package", "suite"]
	to_ret.sort_values('package', inplace=True)
	to_ret.package = to_ret.package.apply(lambda s: s[:-1]) # remove the trailing colon
	return( to_ret)


if len( sys.argv) != 2:
	print("Usage: python process_junit_xml_out.py file_to_append_to")
output_file = sys.argv[1]
# now, do the actual processing
failing_suites = process_fails_file( "fails.csv")
failing_packages = failing_suites.package.unique()
for fp in failing_packages:
	cur_path = "packages/" + fp + "/"
	junit_tests = parse_xml_file(cur_path + "junit-unit-tests.xml")
	relevant_descs = parse_relevant_descs_file(cur_path + "affected_test_descs.txt")
	all_descs = "|".join(relevant_descs.test_desc)
	junit_tests["relevant"] = junit_tests.test_id.str.contains(all_descs)
	junit_tests = junit_tests[junit_tests.relevant].drop(["relevant"], axis=1)
	append_DF_to_file( junit_tests, output_file)

