import pandas
import pyodbc
import sqlalchemy
from datetime import datetime

### Input(s) ###

# Date of file - Include leading 0s
AsOfDate = '10/01/2024'

# File path
FilePath = 'R:\Conversion\Archway\DeptOfBanking'



### Files ###

# Reformat date for use in file name
AsOfDate_File = AsOfDate[-4:] + AsOfDate[:2] + AsOfDate[3:5]

# Business file directory
business = pandas.read_csv(rf'{FilePath}\Business_{AsOfDate_File}.csv')

# People file directory
people = pandas.read_csv(rf'{FilePath}\Person_{AsOfDate_File}.csv')



### Database connection & username ###

# Open database connection
conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=ptcsql807;DATABASE=ExternalData;Trusted_connection=yes', autocommit=True)

# Open database connection
engine = sqlalchemy.create_engine('mssql+pyodbc://ptcsql807/ExternalData?driver=ODBC+Driver+17+for+SQL+Server')

# Create cursor
cur=conn.cursor()
cur.fast_executemany = True

# Grab database username metadata
conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=ptcsql807;DATABASE=ExternalData;Trusted_connection=yes', autocommit=True)
output = pandas.read_sql("SELECT suser_sname() Username", conn)
Username = output['Username'].values[0]



### Adjust file inputs as needed ###

# Replace NaN in Business file with None (prevents error when uploading to database)
business = business.astype(object).where(pandas.notnull(business), None)

# Add date column to front of Business dataframe & metadata to end
business.insert(0,'AsOfDate',AsOfDate)
business['InsertDate'] = datetime.now()
business['UpdateDate'] = datetime.now()
business['UpdateBy'] = Username

# Replace NaN in People file with None (prevents error when uploading to database)
people = people.astype(object).where(pandas.notnull(people), None)

# Add date column to front of People dataframe & metadata to end
people.insert(0,'AsOfDate',AsOfDate)
people['InsertDate'] = datetime.now()
people['UpdateDate'] = datetime.now()
people['UpdateBy'] = Username



### Upload Business data ###

# Truncate Business landing table
cur.execute(f"delete from fincen.Business where AsOfDate = '{AsOfDate}'") 

# Write the people DataFrame to the database
business.to_sql(name='Business', schema='fincen', if_exists='append', con=engine, index=False)

### Upload People data ###

# Truncate People landing table
cur.execute(f"delete from fincen.People where AsOfDate = '{AsOfDate}'") 

# Write the people DataFrame to the database
people.to_sql(name='People', schema='fincen', if_exists='append', con=engine, index=False)



#### Create datasets for final excel output ###

# Run PeopleSearch procedure & return dataset
peoplesearch = pandas.read_sql(f"exec fincen.prc_DOBCHeck '{AsOfDate}','PeopleSearch','N'", conn)

# Replace Nan with two spaces (to prevent error in Check function, doesn't affect values in final excel file)
peoplesearch = peoplesearch.astype(object).where(pandas.notnull(peoplesearch), '  ')

# Create function to check for matches > 1 of first & last names
def Check(row):
    if (row['first_name_matches'] + row['Alias_First_name_Matches'] > 1) and (row['Last_name_matches'] + row['Alias_Last_name_Matches'] > 1):
        return 1

# Add column with results of check to dataset Check column
peoplesearch['Check'] = peoplesearch.apply(Check, axis=1)

# Run BusinessSearch procedure & return dataset
businesssearch = pandas.read_sql(f"exec fincen.prc_DOBCHeck '{AsOfDate}','BusinessSearch','N'", conn)

# Run ComplianceList procedure & return dataset
compliancelist = pandas.read_sql(f"exec fincen.prc_DOBCHeck '{AsOfDate}','ComplianceList','N'", conn)



### Close database connection ###
conn.close()



# Create final excel file
with pandas.ExcelWriter(rf'{FilePath}\Fincen_{AsOfDate_File}.xlsx') as writer:
   
    # Create tabs for file excel file
    people.to_excel(writer, sheet_name="People", index=False)
    business.to_excel(writer, sheet_name="Business", index=False)
    peoplesearch.to_excel(writer, sheet_name="PeopleSearch", index=False)
    businesssearch.to_excel(writer, sheet_name="BusinessSearch", index=False)
    compliancelist.to_excel(writer, sheet_name="ComplianceList", index=False)



### Complete ###
print("Fincen file created successfully!")