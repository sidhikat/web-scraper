from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
import csv


browser = webdriver.Chrome("/Users/sidhikatripathee/Documents/CS/chromedriver")

browser.get('http://www.greatschools.org')  # loads website

city = input("Choose a city to find school in:")
elem = browser.find_element_by_name('locationSearchString')  # Find the search box
elem.send_keys(city + Keys.RETURN)

after_search_url = browser.current_url


# Returns true if the response seems to be HTML, false otherwise
def is_good_response(resp):
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)


# prints log error
def log_error(e):
    print(e)


# Attempts to get the content at `url` by making an HTTP GET request.
# If the content-type of response is some kind of HTML/XML, return the
# text content, otherwise return None
def simple_get(url):
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(after_search_url, str(e)))
        return None

    # Downloads the page where the list of schools is found
    # and returns a list of strings, one per school


# def get_names(url):
#     response = simple_get(url)
#
#     if response is not None:
#         names_element = browser.find_elements_by_xpath(
#             " // a[ @class = 'open-sans_sb mbs font-size-medium rs-schoolName']")
#         names = [x.text for x in names_element]
#         print("School names")
#         print(names, "\n")
#     return names
#
#
# def get_rating(url):
#     response = simple_get(url)
#     ratings2 = []
#     if response is not None:
#         ratings_element = browser.find_elements_by_xpath(" //*[contains(@class, 'col-xs-6 col-sm-4 mvl tac')]")
#         ratings = [x.text for x in ratings_element]
#         for n in ratings:
#             if n is '' or None:
#                 n = "0"
#             n = n[0:1]
#
#             ratings2.append(n)
#         print("School ratings")
#         print(ratings2)
#     return ratings2
#
#
# def get_address(url):
#     response = simple_get(url)
#
#     if response is not None:
#         address_element = browser.find_elements_by_xpath(" //*[contains(@class, 'rs-schoolAddress')]")
#         address = [x.text for x in address_element]
#         print("School addresses")
#         print(address, "\n")
#     return address
#
#
# def get_grades(url):
#     response = simple_get(url)
#
#     if response is not None:
#         grades_element = browser.find_elements_by_xpath("//a[ @class='font-size-small mvm clearfix ptm hidden-xs']")
#         grades = [x.text for x in grades_element]
#         print("Grades")
#         print(grades, "\n")
#     return grades
#
#
#
# names_list=get_names(after_search_url)
# address_list=get_address(after_search_url)
# rating_list=get_rating(after_search_url)
#     # get_grades(after_search_url)

class School:
    name = None
    rating = None
    address = None

    def __init__(self, name, rating, address):
        self.name = name
        self.rating = rating
        self.address = address

def get_boxes(browser):
    box_group = browser.find_element_by_xpath("//html/body/div[6]/div[2]/div[6]/div/div[2]/div")
    box_list = box_group.find_elements_by_xpath("./div[@class='pvm gs-bootstrap js-schoolSearchResult js-schoolSearchResultCompareErrorMessage']")
    return box_list


def get_school(box):
    try:
        return box.find_element_by_class_name('rs-schoolName').text
    except:
        return None


def get_rating(box):
    try:
        return box.find_element_by_xpath(".//*[contains(@class, 'gs-rating circle-rating')]").text
    except:
        return None


def get_address(box):
    try:
        return box.find_element_by_class_name('rs-schoolAddress').text
    except:
        return None


def get_schools(browser):
    box_list = get_boxes(browser)
    schools = []

    for box in box_list:
        name = get_school(box)
        rating = get_rating(box)
        address = get_address(box)
        schools.append(School(name, rating, address))

        for school in schools:
            print(f'name: {school.name}, rating: {school.rating}, address: {school.address}')

    return schools


# Computes collection for all pages


schools = []
while browser.find_element_by_xpath("//*[@rel='next']") is not None:
    schools.extend(get_schools(browser))
    browser.find_element_by_xpath("//a[@rel='next']").click()

browser.quit()

with open('test.csv', 'w', newline='') as fp:
    a= csv.writer(fp)
    a.writerow(["School Name", "Address","Rating"])
    for school in schools:
        result= zip([school.name],[school.address],[school.rating])
        result_list=list(result)
        a.writerows(result_list)

open("test.csv")