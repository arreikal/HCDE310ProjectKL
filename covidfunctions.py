import urllib.parse, urllib.request, urllib.error, json, requests

from datetime import date
from datetime import timedelta

from urllib.request import urlopen


def pretty(obj):
    return json.dumps(obj, sort_keys=True, indent=2)


def prettynosort(obj):
    return json.dumps(obj, sort_keys=False, indent=2)


import statescountries as cs

statedict = cs.statedict
countrydict = cs.ggcountries

baseurl = 'https://disease.sh'


# error 403 without this
class AppURLopener(urllib.request.FancyURLopener):
    version = "Mozilla/5.0"

# req = urllib.request.Request(url,headers={'User-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.1 Safari/605.1.15'}
# thestr = urllib.request.urlopen(req).read().decode('utf-8')
# opener = AppURLopener()

def safe_get_cv(url):
    try:
        url=url.replace(' ', '%20')
        # mypage = opener.open(url)
        req = urllib.request.Request(url, headers={
            'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.1 Safari/605.1.15'})
        thestring = urllib.request.urlopen(req).read().decode('utf-8')
        # thestring = mypage.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        print("The server couldn't fulfill the request.")
        print("Error code: ", e.code)
        return None
    except urllib.error.URLError as e:
        print("We failed to reach a server")
        print("Reason: ", e.reason)
        return None
    except ValueError as e:
        print("We failed to reach a server")
        print("Reason: ", e)
        return None
    thedict = json.loads(thestring)
    return thedict

def safe_get_gg(url):
    try:
        mypage = urlopen(url)
    except urllib.error.URLError as e:
        if hasattr(e,"code"):
            print("The server couldn't fulfill the request.")
            print("Error code: ", e.code)
        elif hasattr(e,'reason'):
            print("We failed to reach a server")
            print("Reason: ", e.reason)
        return None
    except ValueError as e:
        print("We failed to reach a server")
        print("Reason: ", e)
        return None
    except:
        print("Something went wrong :/")
        return None
    try:
        thestring = mypage.read().decode('utf-8')
    except:
        print("fail")
        return None
    return json.loads(thestring)




def get_state_cases(state):
    """Calls the API for a specific state and gets the current data for that state"""
    myurl = baseurl + "/v3/covid-19/states/{state}".format(state=state.lower())
    print(myurl)
    thedict = safe_get_cv(myurl)
    # print(thedict)
    if thedict != None:
        return thedict
    else:
        print("****NONE -- INVALID URL/ SEARCH****")
        return None



def get_country_dict(country):
    """Calls the API for a specific country and gets the current data for that country"""
    myurl = baseurl + "/v3/covid-19/countries/{country}".format(country=country.lower())
    print(myurl)
    thedict = safe_get_cv(myurl)
    # print(thedict)
    if thedict != None:
        return thedict
    else:
        print("****NONE -- INVALID URL/ SEARCH****")
        return None


def get_all_countries():
    """Calls the API for all countries and returns a dictionary with all country data"""
    myurl = baseurl + "/v3/covid-19/countries"
    print(myurl)
    thedict = safe_get_cv(myurl)
    # print(thedict)
    if thedict != None:
        return thedict
    else:
        print("****NONE -- INVALID URL/ SEARCH****")
        return None


def make_country_file(deaths=False):
    """Creates a file with all the countries and their active case per mil in order, and returns a sorted dictionary"""
    thelist = get_all_countries()
    countrydict = {}
    length = len(thelist)
    for i in range(length):
        if thelist[i]["tests"] > 1:
            # if there has been no tests thats really sus
            if deaths:
                countrydict[(thelist[i]["country"])] = thelist[i]["deathsPerOneMillion"]
            else:
                countrydict[(thelist[i]["country"])] = thelist[i]["activePerOneMillion"]
    countrysort = dict(sorted(countrydict.items(), key=lambda item: item[1]))
    with open(("test.csv"), "w") as f:
        f.write("country, active cases per one million\n")
        for country in countrysort:
            f.write("{country},{permil}\n".format(country=country, permil=countrysort[country]))
    return countrysort


def how_safe(actives):
    if actives <= 0:
        return "too_good_to_be_true"
    elif actives < 10:
        return "amazing"
    elif actives < 100:
        return "great"
    elif actives < 500:
        return "good"
    elif actives < 1000:
        return "okay"
    elif actives < 4000:
        return "poor"
    elif actives < 10000:
        return "risky"
    elif actives < 15000:
        return "bad"
    elif actives < 30000:
        return "atrocious"
    else:
        return "abysmal"


def get_current_mil(country):
    if get_country_dict(country) == None:
        return None
    else:
        info = get_country_dict(country)
        return info["activePerOneMillion"]


def get_deaths_mil(country):
    info = get_country_dict(country)
    if info != None:
        return info["deathsPerOneMillion"]
    else:
        return None


ggbaseurl = "https://api.globalgiving.org"
api_key = "be3bba36-23f0-4dbe-b60a-8c70aab2055c"

def get_search_results(keywords, start=0):
    #making url
    ke = keywords.split()
    keys = []
    for key in ke:
        keys.append(key.strip(','))
    query = ""
    if len(keys) == 1:
        query = keys[0]
    elif len(keys) > 1:
        query = keys[0]
        for i in range(len(keys) - 1):
            query += '+' + keys[i + 1]
    if start != 0:
        newstart = 10 * start
        myurl = ggbaseurl + "/api/public/services/search/projects.json?q={query}&start={start}&api_key={api_key}".format(
            api_key=api_key, query=query, start=newstart)
    else:
        myurl = ggbaseurl + "/api/public/services/search/projects.json?q={query}&api_key={api_key}".format(
            api_key=api_key, query=query)
    print(myurl)
    thedict = safe_get_gg(myurl)
    # print(pretty(thedict))
    if thedict != None:
        if "projects" in thedict["search"]["response"].keys():
            projlist = thedict["search"]["response"]["projects"]["project"]
            proj = []
            for p in projlist:
                proj.append(Project(p))
            return proj
        else:
            return None
    else:
        print("****NONE -- INVALID URL/ SEARCH****")
        return None



def get_theme_country(country, start=0):
    country = country.lower()
    if country not in countrydict.keys():
        for cc in countrydict:
            if countrydict[cc] == country:
                country = cc
        # else, just expect an error???
    if start != 0:
        newstart = 10 * start
        myurl = ggbaseurl + "/api/public/services/search/projects.json?q=*&filter=country:{country},theme:covid-19&start={start}&api_key={api_key}".format(
            api_key=api_key, start=newstart, country=country)
    else:
        myurl = ggbaseurl + "/api/public/services/search/projects.json?q=*&filter=country:{country},theme:covid-19&api_key={api_key}".format(
            api_key=api_key, country=country)
    print(myurl)
    thedict = safe_get_gg(myurl)
    # print(pretty(thedict))
    if thedict != None:
        projlist = thedict["search"]["response"]["projects"]["project"]
        proj = []
        for p in projlist:
            proj.append(Project(p))
        return proj
    else:
        print("****NONE -- INVALID URL/ SEARCH****")
        return None



def get_country_results(country, nextid=-999):
    country = country.lower()
    if country not in countrydict.keys():
        for cc in countrydict:
            if countrydict[cc] == country:
                country = cc
        # else, just expect an error???
    if nextid != -999:
        # starting at specific project
        myurl = ggbaseurl + "/api/public/projectservice/countries/{country}/projects.json?nextProjectId={next}&api_key={api_key}".format(
            country=country, api_key=api_key, next=nextid)
    else:
        # just start at any project
        myurl = ggbaseurl + "/api/public/projectservice/countries/{country}/projects.json?api_key={api_key}".format(
            country=country, api_key=api_key)
    print(myurl)
    thedict = safe_get_gg(myurl)
    # print(pretty(thedict))
    if thedict != None:
        proj = []
        if "hasNext" in thedict["projects"].keys():
            if thedict["projects"]["hasNext"] == True:
                # need to remember nextid
                thenextid = thedict["projects"]["nextProjectId"]
                for p in thedict["projects"]["project"]:
                    proj.append(Project(p, next=thenextid))
            else:
                # no need to remember nextid
                for p in thedict["projects"]["project"]:
                    proj.append(Project(p))
        else:
            # no need to remember nextid
            for p in thedict["projects"]["project"]:
                proj.append(Project(p))
        return proj
    else:
        print("****NONE -- INVALID URL/ SEARCH****")
        return None


def get_covid_projects(nextid=-999):
    """Calls the GG API and gets covid related projects"""
    myurl = ggbaseurl + "/api/public/projectservice/themes/covid-19/projects/active.json?api_key={api_key}".format(
        api_key=api_key)
    if nextid != -999:
        myurl = ggbaseurl + "/api/public/projectservice/themes/covid-19/projects/active.json?nextProjectId={nextid}&api_key={api_key}".format(
            nextid=nextid, api_key=api_key)
    print(myurl)
    thedict = safe_get_gg(myurl)
    # print(pretty(thedict))
    if thedict != None:
        proj = []
        if "hasNext" in thedict["projects"].keys():
            if thedict["projects"]["hasNext"] == True:
                # need to remember nextid
                thenextid = thedict["projects"]["nextProjectId"]
                for p in thedict["projects"]["project"]:
                    proj.append(Project(p, next=thenextid))
            else:
                # no need to remember nextid
                for p in thedict["projects"]["project"]:
                    proj.append(Project(p))
        else:
            # no need to remember nextid
            for p in thedict["projects"]["project"]:
                proj.append(Project(p))
        return proj
    else:
        print("****NONE -- INVALID URL/ SEARCH****")
        return None

class Project:
    """This class stores the most important data for a project listing"""

    def __init__(self, projectdict, next=None):
        """Initializes a Project by taking a dictionary of the information for the project"""
        self.title = projectdict["title"]
        self.description = projectdict["summary"]
        if len(self.description) > 250:
            self.description = self.description[0:247] + '...'
        self.url = projectdict["projectLink"]
        self.picurl = projectdict["image"]["imagelink"][2]["url"]
        self.country = projectdict["country"]
        self.countrycode = projectdict["countries"]["country"][0][
            "iso3166CountryCode"]  # check if this works, the country code to search for more country
        self.themes = projectdict["themes"]["theme"]  # list of dictionaries
        self.id = projectdict["id"]  # the project id
        self.goal = projectdict["goal"]  # the projects's money goal
        self.funding = projectdict["funding"]  # how much money the project has raised
        self.activerpermil = get_current_mil(self.country)
        self.next = next
        self.safety = how_safe(self.activerpermil)

    # def __str__(self):
    #     return "{title}\n{summary}\nLocation: {country}\nActive cases per million: {permil} | Safety rating: {safe}\n".format(
    #         title=self.title, summary=self.description, country=self.country, permil=self.activerpermil,
    #         safe=how_safe(self.activerpermil))
    def __str__(self):
        return "<p><b>{title}</b><br>{summary}<br>Location: {country}<br></p><p class='covidinfo'>Active cases per million: {permil} | Safety rating: {safe}<br></p>".format(
            title=self.title, summary=self.description, country=self.country, permil=self.activerpermil,
            safe=how_safe(self.activerpermil))

if __name__ == "__main__":

    print("----")


