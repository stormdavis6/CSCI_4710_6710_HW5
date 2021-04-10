from flask import Flask, render_template, request, redirect, url_for
import util
import os
import glob
from os.path import join, dirname, realpath
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table,Column,Integer,String
from sqlalchemy import MetaData
from sqlalchemy.orm import mapper

app = Flask(__name__)

# evil gloabl variable...
# the data should be obtained from your db
sample_data = {
	'user_data':[
		# index	What country do you live in?	How old are you?	What is your gender?	To what extent do you feel FEAR due to the coronavirus?	To what extent do you feel ANXIOUS due to the coronavirus?	To what extent do you feel ANGRY due to the coronavirus?	To what extent do you feel HAPPY due to the coronavirus?	To what extent do you feel SAD due to the coronavirus?	Which emotion is having the biggest impact on you?	What makes you feel that way?	What brings you the most meaning during the coronavirus outbreak?	What is your occupation?
		[1,"USA",70.0,"Male",2,2,1,2,2,"anticipation of whats going to happen next","Lot's of predictions from differnet resources","Family,Psychologist"],
		[2,"Switzerland",25.0,"Female",3,4,3,4,4,"A mix of awe and anxiety. Awe at how wonderful of a challenge this is for our world to tackle together (especially on issues that have plagued us for decades) and anxiety on how much we may not be thinking about those who are most vulnerable","Reading thought leadership articles and social media","Reading,Global Public Servant (WEF)"],
		[3,"USA",26.0,"Female",3,3,1,4,4,"A mix of happy to be safe and home and sad for people who aren’t","Seeing what’s happening in the news","Family,Student"],
		[4,"USA",11.0,"Male",2,1,5,1,3,"Anger,No sports" ,"Family,Student"],
		[5,"USA",28.0,"Male",4,3,4,1,4,"Anger","a system that cares about profit more than general wellbeing","trying to help","reporter"],
		[6,"USA",24.0,"Female",4,4,5,1,4,"Anger","The US federal government" ,"Friends","Graduate student"],
		[7,"USA",21.0,"Female",4,3,5,3,2,"Anger","People are not being responsible in doing their part in staying in doors. It is causing a major spread in our environment. Due to this spread, I am not allowed to be outdoors or stay in my apartment in Austin. I am very active outside, so this is a challenge for me to stay inside. ","Being alone,Student"],
		[8,"USA",22.0,"Male",3,4,5,2,1,"Anger","Inaction of the people and government","Friends","Janitor"],
		[9,"USA",39.0,"Male",2,2,4,1,2,"Anger","Impacts on day-to-day life","Exercising","Software Engineer"],
		[10,"USA",78.0,"Male",5,5,5,1,1,"Anger","National leadership incompetence","Family","Executive - retired"]
	]
}

column_names = ["index","What country do you live in?","How old are you?","What is your gender?","To what extent do you feel FEAR due to the coronavirus?","To what extent do you feel ANXIOUS due to the coronavirus?","To what extent do you feel ANGRY due to the coronavirus?","To what extent do you feel HAPPY due to the coronavirus?","To what extent do you feel SAD due to the coronavirus?","Which emotion is having the biggest impact on you?","What makes you feel that way?","What brings you the most meaning during the coronavirus outbreak?","What is your occupation?"]

UPLOAD_FOLDER = 'data'
file_path = os.path.join(UPLOAD_FOLDER, 'we_are_not_alone_no_nan.csv')

#SQL Alchemy setup

#Create engine that will allow us to communicate with database
engine=create_engine('sqlite:///we_are_not_alone_dbase.sqlite',echo=False)

#Creating session which is the middle ground to talk to our engine
Session=sessionmaker(bind=engine)
session=Session()

#Map which table in database will be related to each class
Base=declarative_base()

#Create a metadata instance
#A metadata is an object container that will store attributes and name of table
metadata=MetaData(engine)

#Define structure of table
class we_are_not_alone_table(object):
    def __init__(self,number,description,ref_des):
        self.index=index
        self.country=country
        self.age=age
        self.gender=gender
        self.fear=fear
        self.anxious = anxious
        self.angry = angry
        self.happy = happy
        self.sad = sad
        self.emotion = emotion
        self.cause = cause
        self.meaning = meaning
        self.occupation = occupation

    def __repr__(self):
        return f'{self.index,self.country,self.age,self.gender,self.fear,self.anxious,self.angry,self.happy,self.sad,self.emotion,self.cause,self.meaning,self.occupation}'

#Declaring a table
#Defining a function that defines table, we define this function so that we can keep table names dynamic
#That is, we can have multiple tables in database and each table can have a different name
def table_definition(table_name):
    #Define table structure, here table_name varies
    #We want to make table_define available outside function so we declare it as a function attribute
    table_definition.table_define=Table(table_name,metadata,
    Column(column_names[0],Integer,primary_key=True),
    Column(column_names[1],String),
    Column(column_names[2],Integer),
    Column(column_names[3],String),
    Column(column_names[4],Integer),
    Column(column_names[5],Integer),
    Column(column_names[6],Integer),
    Column(column_names[7],Integer),
    Column(column_names[8],Integer),
    Column(column_names[9],String),
    Column(column_names[10],String),
    Column(column_names[11],String),
    Column(column_names[12],String)
    )

    #Create table
    #Note that we used the engine from function
    metadata.create_all(engine)

    #Use mapper to define components of class as well as table definition together at once
    mapper(we_are_not_alone_table,table_definition.table_define,non_primary=True)

#CREATING A DUMMY BLANK TABLE FOR PRIMARY MAPPER
#This avoids error: Class already has a primary mapper defined
#We made non_primary=True in table_definition function mapper
#This is the work around I could use, maybe there is another way

#Define table structure, here table_name varies
table_define_dummy=Table('dummy_table',metadata,
Column(column_names[0],Integer,primary_key=True),
    Column(column_names[1],String),
    Column(column_names[2],Integer),
    Column(column_names[3],String),
    Column(column_names[4],Integer),
    Column(column_names[5],Integer),
    Column(column_names[6],Integer),
    Column(column_names[7],Integer),
    Column(column_names[8],Integer),
    Column(column_names[9],String),
    Column(column_names[10],String),
    Column(column_names[11],String),
    Column(column_names[12],String)
)

#Create table
metadata.create_all(engine)

#Use mapper to define components of class as well as table definition together at once
mapper(we_are_not_alone_table,table_define_dummy)

#This function will create a separate table for each csv file, if you have multiple csv files
#Name of table will be extracted from file name. File name contains product name.
#Each table will be identified by product name
# It will read each excel file in the folder and insert bom into table
def create_table(folder_of_files):

    #Get list of files in folder
    files=glob.glob(os.path.join(folder_of_files,"*.csv"))


    #Loop through all files in list
    for file_name in files:

        #Read file into dataframe
        csv_data=pd.read_csv(file_name)

        #Convert dataframe to list and store in same variable
        csv_data=csv_data.values.tolist()

        #Get table name from file name. This will be our table name.
        table_name_from_file="we_are_not_alone_no_nan"

        #Use table_definition function to define table structure
        table_definition(table_name_from_file)

        #Loop through list of lists, each list in create_bom_table.xls_data is a row
        for row in csv_data:

            #Each element in the list is an attribute for the table class
            #Iterating through rows and inserting into table
            conn=engine.connect()
            conn.execute('INSERT OR IGNORE INTO ' + table_name_from_file + ' Values(?,?,?,?,?,?,?,?,?,?,?,?,?)', row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12])

@app.route('/')
def index():
    list_of_tables = [
        {
            "title": "All User Data"
        },
        {
            "title": "Young Male Data"
        },
        {
            "title": "Middle-Aged or Old Male Data"
        },
        {
            "title": "Young Female Data"
        },
        {
            "title": "Middle-Aged or Old Female Data"
        },
        {
            "title": "Young Male Data USA"
        },
        {
            "title": "Young Male Data Canada"
        },
        {
            "title": "Middle-Aged or Old Male Data USA"
        },
        {
            "title": "Middle-Aged or Old Male Data Canada"
        },
        {
            "title": "Young Female Data USA"
        },
        {
            "title": "Young Female Data Canada"
        },
        {
            "title": "Middle-Aged or Old Female Data USA"
        },
        {
            "title": "Middle-Aged or Old Female Data Canada"
        },
    ]
    #Calling function, argument is path of folder where all CSV files are stored
    create_table(UPLOAD_FOLDER)

    table_df = pd.read_sql_table(
        'we_are_not_alone_no_nan',
        con=engine
    )
    full_data = table_df.values
    list_of_tables[0]["data"] = full_data

    young_male_query = "select * from we_are_not_alone_no_nan where \"How old are you?\" <= 35 AND \"What is your gender?\" = \"Male\""
    young_male_df = pd.read_sql(
            young_male_query,
            con=engine
        )
    young_male_data = young_male_df.values
    labels = util.cluster_user_data(full_data)
    list_of_tables[1]["data"] = young_male_data

    middle_aged_or_old_male_query = "select * from we_are_not_alone_no_nan where \"How old are you?\" >=36 AND \"What is your gender?\" = \"Male\""
    middle_aged_or_old_male_df = pd.read_sql(
            middle_aged_or_old_male_query,
            con=engine
        )
    middle_aged_or_old_male_data = middle_aged_or_old_male_df.values
    list_of_tables[2]["data"] = middle_aged_or_old_male_data

    young_female_query = "select * from we_are_not_alone_no_nan where \"How old are you?\" <= 35 AND \"What is your gender?\" = \"Female\""
    young_female_df = pd.read_sql(
            young_female_query,
            con=engine
        )
    young_female_data = young_female_df.values
    list_of_tables[3]["data"] = young_female_data

    middle_aged_or_old_female_query = "select * from we_are_not_alone_no_nan where \"How old are you?\" >=36 AND \"What is your gender?\" = \"Female\""
    middle_aged_or_old_female_df = pd.read_sql(
            middle_aged_or_old_female_query,
            con=engine
        )
    middle_aged_or_old_female_data = middle_aged_or_old_female_df.values
    list_of_tables[4]["data"] = middle_aged_or_old_female_data

    young_male_usa_query = "select * from we_are_not_alone_no_nan where \"How old are you?\" <= 35 AND \"What is your gender?\" = \"Male\" AND \"What country do you live in?\" = \"USA\""
    young_male_usa_df = pd.read_sql(
            young_male_usa_query,
            con=engine
        )
    young_male_usa_data = young_male_usa_df.values
    list_of_tables[5]["data"] = young_male_usa_data

    young_male_can_query = "select * from we_are_not_alone_no_nan where \"How old are you?\" <= 35 AND \"What is your gender?\" = \"Male\" AND \"What country do you live in?\" = \"Canada\""
    young_male_can_df = pd.read_sql(
            young_male_can_query,
            con=engine
        )
    young_male_can_data = young_male_can_df.values
    list_of_tables[6]["data"] = young_male_can_data

    middle_aged_or_old_male_usa_query = "select * from we_are_not_alone_no_nan where \"How old are you?\" >=36 AND \"What is your gender?\" = \"Male\" AND \"What country do you live in?\" = \"USA\""
    middle_aged_or_old_male_usa_df = pd.read_sql(
            middle_aged_or_old_male_usa_query,
            con=engine
        )
    middle_aged_or_old_male_usa_data = middle_aged_or_old_male_usa_df.values
    list_of_tables[7]["data"] = middle_aged_or_old_male_usa_data

    middle_aged_or_old_male_can_query = "select * from we_are_not_alone_no_nan where \"How old are you?\" >=36 AND \"What is your gender?\" = \"Male\" AND \"What country do you live in?\" = \"Canada\""
    middle_aged_or_old_male_can_df = pd.read_sql(
            middle_aged_or_old_male_can_query,
            con=engine
        )
    middle_aged_or_old_male_can_data = middle_aged_or_old_male_can_df.values
    list_of_tables[8]["data"] = middle_aged_or_old_male_can_data

    young_female_usa_query = "select * from we_are_not_alone_no_nan where \"How old are you?\" <= 35 AND \"What is your gender?\" = \"Female\" AND \"What country do you live in?\" = \"USA\""
    young_female_usa_df = pd.read_sql(
            young_female_usa_query,
            con=engine
        )
    young_female_usa_data = young_female_usa_df.values
    list_of_tables[9]["data"] = young_female_usa_data

    young_female_can_query = "select * from we_are_not_alone_no_nan where \"How old are you?\" <= 35 AND \"What is your gender?\" = \"Female\" AND \"What country do you live in?\" = \"Canada\""
    young_female_can_df = pd.read_sql(
            young_female_can_query,
            con=engine
        )
    young_female_can_data = young_female_can_df.values
    list_of_tables[10]["data"] = young_female_can_data

    middle_aged_or_old_female_usa_query = "select * from we_are_not_alone_no_nan where \"How old are you?\" >=36 AND \"What is your gender?\" = \"Female\" AND \"What country do you live in?\" = \"USA\""
    middle_aged_or_old_female_usa_df = pd.read_sql(
            middle_aged_or_old_female_usa_query,
            con=engine
        )
    middle_aged_or_old_female_usa_data = middle_aged_or_old_female_usa_df.values
    list_of_tables[11]["data"] = middle_aged_or_old_female_usa_data

    middle_aged_or_old_female_can_query = "select * from we_are_not_alone_no_nan where \"How old are you?\" >=36 AND \"What is your gender?\" = \"Female\" AND \"What country do you live in?\" = \"Canada\""
    middle_aged_or_old_female_can_df = pd.read_sql(
            middle_aged_or_old_female_can_query,
            con=engine
        )
    middle_aged_or_old_female_can_data = middle_aged_or_old_female_can_df.values
    list_of_tables[12]["data"] = middle_aged_or_old_female_can_data

    for item in list_of_tables[5: ]:
        if len(item["data"]) > 10:

            labels = util.cluster_user_data(item["data"])

            groups = util.split_user_data(item["data"], labels)

            for i, table in enumerate(groups):
                dict = {
                    "title": "%s KMeans Split #%d" % (item["title"], i+1),
                    "data": []
                }
                dict["data"] = table
                print(type(table))
                print(table)
                list_of_tables += [dict]

    return render_template('index.html', labels_html=labels, column_html=column_names, data_html=list_of_tables)

if __name__ == '__main__':
	# set debug mode
    app.debug = True
    # your local machine ip
    ip = '127.0.0.1'
    app.run(host=ip)