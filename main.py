#!/usr/bin/env python

from flask import Flask, render_template, request
import urllib.parse, urllib.request, urllib.error, json, requests
import logging

#important methods
import covidfunctions as cf

app = Flask(__name__)

#initial, total, last
list1 = cf.get_covid_projects()
listrecorder= [list1,list1,list1]


@app.route("/", methods=["POST","GET"])
def main_handler():
    # app.logger.info("In MainHandler")
    # update_vars()
    if request.method == "POST":
        if listrecorder != None:
            if listrecorder[0]!= None:
                if listrecorder[1] != listrecorder[0]:
                    #has already been called
                    if listrecorder[2][0].next != None:
                        nextlist = cf.get_covid_projects(nextid=listrecorder[2][0].next)
                        listrecorder[1] += nextlist
                        listrecorder[2] = nextlist
                    else:
                        #no more results
                        return render_template('index.html', page_title="No More Results", the_data=listrecorder[2],
                                               errormsg="No More Results")
                else:
                    #first time more results has been called
                    if listrecorder[0][0].next != None:
                        #there are more results
                        nextlist = cf.get_covid_projects(nextid=listrecorder[0][0].next)
                        listrecorder[1] += nextlist
                        listrecorder[2] = nextlist
                    else:
                        #no more results
                        return render_template('index.html', page_title="No More Results", the_data=listrecorder[0],
                                               errormsg="No More Results")
                return render_template('index.html', page_title="More Results", the_data=listrecorder[1], errormsg=None)
            else:
                # there are no results
                return render_template('index.html', page_title="No Results", the_data=None,errormsg="No Results")
        else:
            #there are no results
            return render_template('index.html', page_title="No Results", the_data=None,
                                   errormsg="No Results")

    else:
        #get
        return render_template('index.html',page_title="Inputting", the_data=listrecorder[0], errormsg=None)



@app.route("/indexcountry")
def greet_response_handler():
    # app.logger.info(request.args.get('username'))
    country = request.args.get('country')
    if country:
    #     #form filled out

        projectlist = cf.get_country_results(country)

        return render_template('indexcountry.html',
                                page_title="Search Results for {}".format(country),
                                the_data=projectlist, deaths=cf.get_deaths_mil
        )
    else:
        return render_template('index.html', page_title="Please Input", errormsg="Please input a country")



if __name__ == "__main__":
    # Used when running locally only. 
	# When deploying to Google AppEngine, a webserver process will
	# serve your app. 
    app.run(host="localhost", port=8080, debug=True)
