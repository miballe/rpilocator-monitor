from distutils.command import config
import os
import time
import requests as r
import pandas as pd
import logging
from sys import stdout

# Logger initialisation
logger = logging.getLogger('rpimon')
logger.setLevel(logging.INFO) # set logger level
logFormatter = logging.Formatter("%(asctime)s [%(levelname)s]: %(funcName)s ¦ %(message)s")
console_handler = logging.StreamHandler(stdout)
console_handler.setFormatter(logFormatter)
logger.addHandler(console_handler)
file_handler = logging.FileHandler("/log/rpilocatormon.log", 'a+')
file_handler.setFormatter(logFormatter)
logger.addHandler(file_handler)

logger.info('*** Script Start ***')

# Constants
iftt_webhook_base = 'https://maker.ifttt.com/trigger'
rpiloc_url = 'https://rpilocator.com/feed/'

# From Config
event_delta_mins = int(os.getenv('EVENT_DELTA_MINS', 5))
model_filter = os.getenv('MODEL_FILTER', 'RPi')
ifttt_alert_name = os.getenv('IFTTT_ALERT_NAME', 'my_alert')
ifttt_key = os.getenv('IFTTT_KEY', None)
if ifttt_key is None:
    logger.error('IFTTT_KEY environment variable not defined!')
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
    logger.info('** Main Loop Start **')
    loop_n = 0
    while(True):
        logger.info(f'* Loop {loop_n}')
        if(file_test_mode):
            rpidf = pd.read_xml('app/sample.xml', xpath='.//item')
            logger.debug(f'Found {rpidf.shape[0]} records in the sample.xml file')
        else:
            rpl_resp = r.get(rpiloc_url, headers={'accept': '*/*', 'user-agent': 'curl/7.68.0'})
            rpidf = pd.read_xml(rpl_resp.text, xpath='.//item')
            logger.info(f'Found {rpidf.shape[0]} records in the RPiLocator site')
        rpidf['ts'] = pd.to_datetime(rpidf['pubDate'], format='%a, %d %b %Y %H:%M:%S %Z')
        rpidf = rpidf[rpidf['description'].str.contains(model_filter)]
        ts_delta_ago = pd.to_datetime(pd.Timestamp('now', tz='GMT') - pd.Timedelta(event_delta_mins, 'minutes')).strftime('%Y-%m-%d %H:%M:%S')
        ts_delta_ago += ' GMT'
        rpidf = rpidf[rpidf['ts'] > ts_delta_ago]

        logger.info(f'Found {rpidf.shape[0]} items to send alerts')

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
                logger.info(f'Notification sent to IFTTT with code {ifttt_resp.status_code}')
        
        time.sleep(sleep_time_secs)
        loop_n += 1


if __name__ == "__main__":
    check_stock()
