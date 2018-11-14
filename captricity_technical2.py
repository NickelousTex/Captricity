import json, requests, csv
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
        if not child_branch['reject_reasons']: # Verify if it's a reject batch pass if so, else return  jobs id
            job_list.extend(child_branch['job_ids'])
        else:
            pass

    return job_list

def get_job_info(job_id, headers):
    '''
    Reads in the job information, while providing API key, and returns a list format csv file
    '''
    url = 'https://{}/api/v1/job/{}/csv/'.format(BASE_URL, job_id)
    job = requests.get(url, headers=headers)
    job_content = job.content.decode('utf-8')
    cr = csv.reader(job_content.splitlines(), delimiter=',')
    my_list = list(cr)
    return my_list

def format_date(old_date):
    '''
    Verify if date is before today, else subtract 100 years(year seems to be only issue, but could check month and day as well), return in
    requested format
    '''
    if old_date > old_date.today():
        old_date -= timedelta(days=365.25*100)
    else:
        pass
    return '{}-{:02d}-{:02d}'.format(old_date.year, old_date.month, old_date.day) # Ensure double digit month/day formating

#Simple checker
def convert_date(try_date):
    '''
    try various date patterns, if none then return impossible
    '''
    # Can always add in more potential date patterns, also can put in order of most common to cut down slightly on run time
    date_patterns = ["%m/%d/%Y", "%m%d%y", '%m%d%Y', '%m%d%y' '%m %d %Y','%Y-%m-%d', '%m %d %y', '%m %d %Y']
    if try_date == '--blank--':
        return '--blank--'
    else:
        for pattern in date_patterns:
            try:
                datetime.strptime(try_date, pattern).date()
                return format_date(datetime.strptime(try_date, pattern).date())
            except:
                pass
    return '--impossible--'

def write_to_csv(csv_rows):
    '''
    write resulting csv lists to file if needed
    '''
    writer = csv.writer(open("captricity2_csv.csv", 'w'))
    for row in csv_rows:
        writer.writerow(row)


if __name__ == '__main__':
    # API Info
    Batch_ID= 2995585
    API_token =  {'Captricity-API-Token': '435c308483e040fe9928418703216584'}
    BASE_URL = 'shreddr.captricity.com'

    # Pull batch info
    Parent_batch = get_batch_info(Batch_ID,API_token)
    job_list = get_children_job_info(Parent_batch)

    # Pull Job Info
    job_text = get_job_info(job_list[0],API_token)#Note this should be changed for later if we run into mutiple job lists

    # Convert DateTimes to correct format and save (This assumes we know  where the column will be indexed)
    for column in job_text[1:]:
        column[4]=convert_date(column[4])
        column[7]=convert_date(column[7])
        column[8]=convert_date(column[8])
    # Return in place:
    #return job_text

    # Save to file:
    write_to_csv(job_text)
