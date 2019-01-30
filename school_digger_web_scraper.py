from selenium.webdriver.common.keys import Keys
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv


browser = webdriver.Chrome("/Users/sidhikatripathee 1/Documents/CS (CoderKids)/chromedriver 2")

browser.get('https://www.schooldigger.com') # loads website


city = input("Choose a city to find school in:")
elem = browser.find_element_by_name('ctl00$ContentPlaceHolder1$HomePageSearch$txtHPAC')  # Find the search box
elem.send_keys(city + Keys.RETURN)
home_url=browser.current_url

#gets web address after search
form = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.ID, 'ctl00_ContentPlaceHolder1_SchoolListWidget_liTabTable')))
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

#click table
form = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.ID, 'ctl00_ContentPlaceHolder1_SchoolListWidget_liTabTable')))
form.find_element_by_id("ctl00_ContentPlaceHolder1_SchoolListWidget_liTabTable").click()

#click sort
form1 = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.ID, 'tabSchooList')))
form1.find_element_by_xpath('//*[@id="tabSchooList"]/thead/tr[2]/th[8]').click()  #acesending sort
form1.find_element_by_xpath('//*[@id="tabSchooList"]/thead/tr[2]/th[8]').click()  #desending sort

#gets school name
def get_names(url):
    show=browser.find_element_by_name("tabSchooList_length")
    show.send_keys("a"+Keys.RETURN)
    response = simple_get(url)
    if response is not None:
        names_element = browser.find_elements_by_class_name("sName")
        names = [x.text for x in names_element]
    return names

#gets table values of each row
def get_grades(url):
    row_list=[]
    response = simple_get(url)
    if response is not None:
        table_element = browser.find_element_by_id("tabSchooList")# gets entire table
        tr_collection= table_element.find_elements_by_xpath('./tbody') #gets the body of table
        for tr_element in tr_collection:
            td_collection = tr_element.find_elements_by_xpath('./tr') #gets the row
            for tdElement in td_collection:
                row_list.append(tdElement.text)

    return row_list

#gets free/reduced lunch percentage
def get_reduced_lunch():
    free_elements= browser.find_elements_by_xpath('//*[@id="aspnetForm"]/div[5]/div[1]/div[3]/div[1]/div[1]/div/div/div/div[2]/span[3]')
    lunch_list=[x.text for x in free_elements]
    return lunch_list

school_list=[]
school_length= len(get_names(after_search_url))
#returns name, type,address,phone num, ranking for each school's website

def get_info(url):
    school_info_list=[]
    names=[]
    type = []
    phone = []
    address = []
    ranking=[]
    lunch_list=[]
    split=""
    response = simple_get(url)
    if response is not None:
        #find names
        names_element = browser.find_elements_by_xpath('//*[@id="aspnetForm"]/div[5]/div[1]/div[3]/h1/span')
        names = [x.text for x in names_element]
        school_info_list.extend(names)

        info_element = browser.find_elements_by_xpath('//*[@id="aspnetForm"]/div[5]/div[1]/div[3]/div[1]/div[1]/div/div/div/div[1]')
        info = [x.text for x in info_element]
        for element in info:
            split=element.split("\n") #splits left column

        if len(split) >=5 :
            (type.append(split[0]))
            (address.append(split[2]+split[3]))
            (phone.append(split[5]))
            ranking.append(split[-1])
            school_info_list.extend(type)
            school_info_list.extend(address)
            school_info_list.extend(phone)
            school_info_list.extend(ranking)
        else:
            return ["N/A"]
        lunch_list=get_reduced_lunch()
        school_info_list.extend(lunch_list)

    return school_info_list


def main():
    get_names(after_search_url)
    #list_of_rows = get_grades(after_search_url)
    teleport(after_search_url)


    #transport to csv
    with open('school_list.csv', 'w', newline='') as fp:

        a = csv.writer(fp)
        a.writerow(["School Name", "School Type","Address", "Phone Number","Ranking","Free/Reduced Lunch"])
        for i in range(0,len(school_list)):
            print(school_list[i])
            if(len((school_list[i]))>2):
                data=[]
                for c in range(0,6):
                    data.append(school_list[i][c])

                data_list=[data[0],data[1],data[2],data[3],
                           data[4],data[5]]
            else:
                data_list=[school_list[i]]

            a.writerow(data_list)



    open("school_list.csv")



#transport between different school pages
#returns a school list with all its information
def teleport(url):
    browser.get(after_search_url)
    for i in range(1,school_length+1):
        if (i >= 100):
            form = WebDriverWait(browser, 10).until(
                EC.visibility_of_element_located((By.ID, 'ctl00_ContentPlaceHolder1_SchoolListWidget_liTabTable')))
            form.find_element_by_xpath('//*[@id="alertMapWidget"]/a').click()  # clicks load all
        print(i)
        form = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.ID, 'divList')))
        xPath='//*[@id="divList"]/div/div['+((str)(i))+']/div[1]/div/div[1]/h3/a'
        form.find_element_by_xpath((str)(xPath)).click()
        school_list.extend([get_info(url)])

        browser.get(after_search_url)

    return school_list


main()
browser.quit()