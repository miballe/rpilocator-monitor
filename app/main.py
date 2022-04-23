import os
import time
import requests as r
import pandas as pd
import logging

logging.basicConfig(filename='/log/rpilocatormon.log', \
                    filemode='w', \
                    format='%(asctime)s - %(levelname)s - %(message)s',\
                    level=logging.INFO)

logging.info('*** Script Start ***')

# Constants
iftt_webhook_base = 'https://maker.ifttt.com/trigger'
rpiloc_url = 'https://rpilocator.com/feed/'

# From Config
event_delta_mins = int(os.getenv('EVENT_DELTA_MINS', 5))
model_filter = os.getenv('MODEL_FILTER', 'RPi')
ifttt_alert_name = os.getenv('IFTTT_ALERT_NAME', 'my_alert')
ifttt_key = os.getenv('IFTTT_KEY', None)
if ifttt_key is None:
    raise RuntimeError('IFTTT_KEY environment variable not defined!')
file_test_mode = os.getenv('FILE_TEST_MODE', False)
sleep_time_secs = 300
if type(file_test_mode) == str:
    if file_test_mode.lower() == 'true':
        file_test_mode = True
        sleep_time_secs = 5
    else:
        file_test_mode = False
sleep_time_secs = int(os.getenv('SLEEP_TIME_SECS', sleep_time_secs))

# Global calculated values
iftt_full_url = f'{iftt_webhook_base}/{ifttt_alert_name}/with/key/{ifttt_key}'

def check_stock():
    logging.info('** Main Loop Start **')
    while(True):
        loop_n = 0
        logging.info(f'* Loop {loop_n}')
        if(file_test_mode):
            rpidf = pd.read_xml('./sample.xml', xpath='.//item')
            logging.debug(f'- From file {rpidf.shape[0]} records')
        else:
            rpl_resp = r.get(rpiloc_url, headers={'accept': '*/*', 'user-agent': 'curl/7.68.0'})
            rpidf = pd.read_xml(rpl_resp.text, xpath='.//item')
            logging.info(f'- From site {rpidf.shape[0]} records')
        rpidf['ts'] = pd.to_datetime(rpidf['pubDate'], format='%a, %d %b %Y %H:%M:%S %Z')
        rpidf = rpidf[rpidf['description'].str.contains(model_filter)]
        ts_delta_ago = pd.to_datetime(pd.Timestamp('now', tz='GMT') - pd.Timedelta(event_delta_mins, 'minutes')).strftime('%Y-%m-%d %H:%M:%S')
        ts_delta_ago += ' GMT'
        rpidf = rpidf[rpidf['ts'] > ts_delta_ago]

        logging.info(f'Found {rpidf.shape[0]} items for alerts')

        if rpidf.shape[0] > 0:
            for index, row in rpidf.iterrows():
                msg = {
                    "value1": "Pi!",
                    "value2": row['title'],
                    "value3": row['link']
                }
                hdrs = {
                    'Content-Type': 'application/json'
                }
                ifttt_resp = r.post(iftt_full_url, json=msg, headers=hdrs)
                logging.info(f'Notification sent to IFTTT with code {ifttt_resp.status_code}')
        
        time.sleep(sleep_time_secs)
        loop_n += 1


if __name__ == "__main__":
    check_stock()

