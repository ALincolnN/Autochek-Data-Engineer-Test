# Autochek Data Engineer Technical Test.

The Technical Test consists of two parts; *Problem 1* and *Problem 2*.

The first question has been done using SQL in PostgreSQL as the RDMS while the second question has been done using Python
for scripting and Apache Airflow for orchestration and scheduling.

Clone the project from GitHub and the file structure for the project will be:

         ├── Autochek-Data-Engineering-Interview            
            ├── Problem1
            │      ├── autochek.sql
            │      ├── borrower_table.csv
            │      ├── Final.xls
            │      ├── loan_repayment.csv
            │      ├── loan_table.csv
            │      ├── payment_schedule.csv
            ├── Problem2
            │      ├── dags
            │      │     ├── runner.py
            │      ├── logs
            │      │      ├──
            ├      ├── plugins
            │      │      ├──
            │      ├── reports
            │      │      ├── exchange
            │      ├── .env
            │      ├── docker-compose.yaml
            │      ├── Dockerfile
            │      ├── requirements.txt
            │      ├── scrapper.py
            ├── .gitignore
            ├── README.md
            
The reason for the structure is to ensure that different parts of the assignment are logically separated for ease of access.

**Problem1** contains file data for the first question in .csv and .xls formats and a .sql file for the queries used to work on the problem.

**Problem2** should contain folders namely dags, logs, plugins and reports which are volumes mounted by the containers running in docker to synchronize output from the containers to the host machine.
You should create a .env file in this directory to hold the environment variables you need in order to work on the question. The variables here being **AIRFLOW_UID**, **ACCOUNT_ID** and **API_KEY**.
I will explain where to get these in a few. There is the **docker-compose.yaml** file that has definitions for the services and containers to be dockerized.
**Dockerfile** has been defined holding necessary instructions for building the docker image being used by the airflow containers.
**requirements.txt** has all the required dependencies for the scripts running in the containers.
**scrapper.py** is the script written in python that handles the logic of getting currency exchange data and saving it to a csv file that is stored at the reports/ directory.

**.gitignore** Has items that are being excluded from being tracked by Git Version Control.

**README.md** Is this file you are reading that contains instructions on how the project has been structured and how the problems have been tackled.

**Note:** ***The following assumptions have been made;***

You already have PostgreSQL installed on your system.

You have the data already in your tables.

You have docker already installed in your system.

## Problem 1.
I have included ***autochek.sql*** file which has the queries run during attempting the problem.

The first section includes statements I used to create tables for the problem.

Data was inserted to the tables using the psql utility command ```\COPY table(column1, columnN) FROM '/path/to/respective/file/name.csv' DELIMITER ',' CSV HEADER```* 
to copy contents of the provided csv files to the tables respectively.

***Section 2*** handles creates a summary the customers, the loans they currently have, the dates they have been scheduled to repay and how frequent they are paying back.

The frequency has been generated by getting the difference between a date and its subsequent date which have been ordered in descending order using date_paid column of the loan_repayment table 
and is in days.

***Section 3*** shows how many times a customer has failed to pay a loan they have. The result is grouped by borrower id and loan id since a customer can have multiple loans but each loan id is unique in the loans_table.

The result has been achieved by getting the number of payments the customer has made, grouped by loan id, getting the sum of dates each loan is scheduled to be paid, then creating a join with borrower_table and 
loan_table with the earlier common table expressions.

In this case, the missed_payments were 0 for each loan since from the dataset provided, all the payments were made in the scheduled dates.

***Section 4*** is about getting the result for the columns provided in the figure for question 1. 

The rationale behind the solution provided in *Final.xls* is getting the most recent loan payment for each 
loan, getting the last scheduled payment for a loan and performing the necessary joins. 

The final result set is being grouped by loan_id and borrower_id, essentially giving a summary of all the distinct loan_ids belonging 
to borrowers. *current_days_past_due* is a result of deducting the last date the loan was paid from the last scheduled day for the loan, 0 as in the result because the last payment for each loan was made on the expected payment date.

*last_due_date* has been given as the last scheduled date for a loan in the payment_schedule table. 

*last_repayment_date* is given as the last day instalment was made for a loan. 

*amount_at_risk* has been given as the difference between the expected last payment and the actual last payment made.

As indicated above, **Problem1/Final.xls** has the result for Section 4.


## Problem 2
### Script
The assignment is to create a script that gets exchange rates for the currencies for 7 countries namely Kenya, Uganda, Nigeria, Morocco, Ghana, Cote D'Ivoire and Egypt.

I have implemented the above using Python to script and scheduling using Apache Airflow. In Problem2/dags is where runner.py is located and is basically the script used to schedule the script Problem2/scrapper.py.
Essentially, scrapper.py is where all the magic happens.

The script *scrapper.py* first imports the necessary dependencies for the project, imports API_KEY, ACCOUNT_ID, AIRFLOW_UID from the .env file that you created at the directory Problem2/.

I have provided the currencies as an array of string items2, in their ISO 4217 currency codes.

I join the list of currency codes and assign them to a variable *params*; provide the url to get data from as https://xecdapi.xe.com/v1/ which also is the official Swagger UI documentation for Xecd.
The *convert_from.json* means that you want to access the convert_from endpoint and return the data in Json format.

I am using the requests.get() method from the requests package available for python to send a HTTP GET method to the url while supplying authentication details as a tuple for the method. I am passing the content of the params 
variable created earlier as a value for the key 'to' which takes comma separated values as a string, for the Xe endpoint.

I am later parsing the data to json format in order to be able to access the json encoded response from the API.

I have opted to use timestamp for when the data dictionary is being created since the timestamp provided from xe doesn't contain a valid Hour, Minute and Second value.

For each currency that is being checked for its conversion rate against the USD, a conversion from the currency to USD is also being fetched in order to avoid inaccuracies gotten from calculating them.

The data dictionary is then being appended to a list called data that is finally written to a csv file called currency_conversion_data.csv.

The reason there is a check for */opt/airflow/reports/* is because that is the directory that is defined in the containers. If the directory exists, the script knows that it is running inside docker hence no need to create 
the directory since it is already created by the containers., otherwise it is created on the working directory of the script.

By doing the above, the new data will always be appended to the existing data in the csv file.


### Scheduling
Scheduling has been achieved through Apache Airflow with the cron expression '0 1,23 * * *', signifying that it will run at 2300hrs which is 11pm and 0100hrs that is 1am.

Scheduling has been defined on the file *runner.py* where the Direct Acyclic Graph(DAG) and tasks are defined

### Running docker
You need to have docker installed on your system

Once you have cloned the repository to your machine and ensured that docker-compose and docker service is installed and active, change the directory to Problem2, since this is where the resources necessary for
docker and the script are located.

Create a file called .env in this directory and define 'API_KEY' and 'ACCOUNT_ID' and assign the values provided from the xecd dashboard that you get when you create an account.

Run the command ```echo -e "\nAIRFLOW_UID=$(id -u)" > .env``` as a non-root account user so that the user who runs the containers is also set to non-root, for permission purposes.

Build the image first using ```docker build -t airflow .```, meaning that docker is going to use the Dockerfile in the same directory.

After the image is built, run the command ```docker compose up airflow-init```to initialize the containers and database defined in the .yaml file. This will create a user called 'airflow' with password 'airflow' 
to be used the web server on '0.0.0.0:8080'.

After the steps are done, run ```docker compose up``` to start the containers.

Access the webserver using 'localhost' and port '8080' and log in using the credentials mentioned earlier.

Once logged in, you should unpause the dag called 'data_scrapper' by clicking the toggle button and for testing purposes, click the trigger DAG option on the action buttons in order to see what happens.

The output will be saved on the directory you are in i.e Problem2/reports/ as currency_conversion_data.csv


The .yaml file being used above is a tweaked version of the official .yaml file provided by airflow, with changes tailored for our case scenario.





***That's it for the assignment. Thank you***







