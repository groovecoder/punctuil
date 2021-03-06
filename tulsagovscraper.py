###
# A module containing the functions to scrape the necessary information
# from the Tulsa City Council's website.
# Service Hackathon - 2/22/14 - Ian Riley & Luke Crouch
###
from bs4 import BeautifulSoup
import requests
import re
import time

# the url for the Tulsa City Council website
COUNCIL_URL_ROOT = "http://www.tulsacouncil.org/inc/search"

##
# Scrapes the agenda information for the given meeting. A url must
# be provided to access the meeting agenda. The url can be pulled
# from the reference contained in the meeting information.
##
def scrape_agenda(meeting_agenda_url):
    # send a POST request for the meeting agenda
    meeting_agenda = requests.get(meeting_agenda_url)
    # load the content of the page into a BeautifulSoup object(a html parser)
    parser = BeautifulSoup(meeting_agenda.content)
    # agenda points are organized numerically, therefore we can locate the information
    # for each point in the agenda using a regex pattern defined to match numbers, and
    # then pulling the subsequent lines
    patt  = re.compile(r'\d+\.')

    # instantialize a list to store the agenda information
    agenda_information = []
    agenda_point = 0
    # the agenda points are all contained in table data elements, so we pull
    # all of the table table elements to locate the elements with the information
    # that we need
    for element in parser.find_all('td'):
        # match the regex pattern to locate the numbered bulletin points
        if re.match(patt, element.get_text()):
            # append the agenda information for each point into the data structure
            agenda_information.append([])
            if element.find_previous_sibling() == None:
                # append the section information
                agenda_information[agenda_point].append(element.get_text().strip())
                if element.find_next_sibling() == None:
                    agenda_information.pop(len(agenda_information)-1)
                    continue
                # append the item number
                agenda_information[agenda_point].append(int(re.search(r'\d+', element.find_next_sibling().get_text().strip()).group(0)))
            else:
                # append the section information
                agenda_information[agenda_point].append(element.find_previous_sibling().get_text().strip())
                # append the item number
                agenda_information[agenda_point].append(int(re.search(r'\d+', element.get_text().strip()).group(0)))
            # append the text, minutes, and backup
            for point_info in element.find_next_siblings('td', None, None, 3):
                agenda_information[agenda_point].append(point_info.get_text().strip())
            for index in range(5-len(agenda_information[agenda_point])):
                agenda_information[agenda_point].append('')
            agenda_point += 1
    
    # return the results
    return agenda_information
##
# The Tulsa City Council page for their meetings is segmented by month and year. Each meeting
# contains a date, time, topic, and reference to the agenda information. This function requests
# and returns a list of the meetings for the current month in the current year.
##
def get_meeting_list():
    # the url extension for the meeting list page
    MEETING_LIST_URL = '%s/meeting_list.php' % COUNCIL_URL_ROOT
    # the paramters for the current month and year to attach to the POST request
    date_params = {"MeetingMonth": time.strftime('%m'), "MeetingYear": time.strftime('%Y'), "Submit": "Go"}
    # send a POST request for the meeting list
    meeting_list = requests.get(MEETING_LIST_URL, params=date_params)
    # load the meeting list into a BeautifulSoup object(an html parser)
    parser = BeautifulSoup(meeting_list.content)

    # the data structure containing the list of meetings
    meetings = []
    # each meeting is contained in a table data element,
    # use the parser to pull all the table data elements,
    # and append the meeting information to the internal data structure
    for meet in parser.find_all('td'):
        meetings.append({'href': meet.a['href'],
                             'text': meet.get_text().strip()})
    # return the data structure of meetings
    return meetings
