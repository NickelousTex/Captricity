import json, requests, csv
import pandas as pd
from contextlib import closing
from datetime import timedelta, date, datetime

def get_batch_info(batch_id, headers):
    '''
    Returns batch information in JSON format from Captricity API
    '''
    url = 'https://{}/api/v1/batch/{}'.format(BASE_URL, batch_id)
    batch = requests.get(url, headers=headers)
    return json.loads(batch.text)

def get_children_job_info(parent_batch):
    '''
    Returns list of job ids from valid children batches
    '''
    job_list = []
    for ids in Parent_batch['children_ids']:
        child_branch = get_batch_info(ids, API_token)
        if not child_branch['reject_reasons']: #verify if it's a reject batch pass if so, else return  jobs id
            job_list.extend(child_branch['job_ids'])
        else:
            pass

    return job_list

def get_job_info(job_id, headers):
    '''
    Returns text version from job pull request
    '''
    url = 'https://{}/api/v1/job/{}/csv/'.format(BASE_URL, job_id)
    job = requests.get(url, headers=headers)
    return job.text

def read_csv_url(job_text):
    '''
    Read dataframe into memory
    '''
    reader = csv.reader(job_text.split('\n'), delimiter=',')
    df= pd.DataFrame([row for row in reader])
    df = df.rename(columns=df.iloc[0]).drop(df.index[0])
    return df

def convert_datetime(df, col_name):
    '''
    Converts pandas series items into datetime, and checks for errors
    '''
    new_dates = pd.to_datetime(df[col_name], errors= 'coerce')
    for date in new_dates:
        if not datetime.date:
            pass
        elif date > datetime.utcnow():
            new_dates.replace(date, date - timedelta(days=365.25*100), inplace=True)
        else:
            pass

    return(new_dates)

if __name__ == '__main__':
    #API Info
    Batch_ID= 2995585
    API_token =  {'Captricity-API-Token': '435c308483e040fe9928418703216584'}
    BASE_URL = 'shreddr.captricity.com'

    #Pull batch info
    Parent_batch = get_batch_info(Batch_ID,API_token)
    job_list = get_children_job_info(Parent_batch)

    #Pull Job Info
    job_text = get_job_info(job_list[0],API_token)#Note this should be changed for later if we run into mutiple job lists

    # Convert DateTimes to correct format and save
    df = read_csv_url(job_text)
    df['patient_dob'] = convert_datetime(df, 'patient_dob')
    df['dos_from'] = convert_datetime(df, 'dos_from')
    df['dos_to'] = convert_datetime(df, 'dos_to')
    df.to_csv('my_save_job.csv') #Saves job, could remove for display
