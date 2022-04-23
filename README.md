# RPi Locator Monitor

RPiLocator monitor and notifier. Detect when a specific Raspberry Pi model is available and sends a notification via a WebHook in IFTTT. In this project, the notification is received in a mobile phone.

This project is designed to monitor the RSS feed in the site [rpilocator.com](https://rpilocator.com), and detect a stock availability change within minutes. The detection is based in a window of time defined by a frequency of execution and a range of time to look backwards. For example, if the script executes every 5 minutes, it can be set to detect changes within the last 5 minutes.

configuration
=============

The following environment variables can be set:

* **EVENT_DELTA_MINS**: Range of time to scan for stock changes. The default is 10 minutes
* **MODEL_FILTER**: String to get notification only about the model of interest. The default value is "RPi". Other suggested values can be "Model B", "CM4", "Zero 2", etc.
* **IFTTT_ALERT_NAME**: Alert name defined in the IFTTT Webhook service. The default value is "my_alert".
* **IFTTT_KEY**: IFTTT Webhook key with the format "ep3jdTg7T6G5yF-ihegrQq". The default value is None. If this value is not set, an exception will be triggered and the monitor stops.
* **FILE_TEST_MODE**: Debug value to use a local file to validate conditions. The default value is "false".
* **SLEEP_TIME_SECS**: Wait time between stock checks. The default value is 300 seconds (5 minutes) when chekcing the live website. The default value when debugging using the XML file is 5 seconds.

Deployment
==========

The easiest way is using the docker image and docker-compose or Portainer.

```yaml
version: '3.9'

services:
  listener:
    container_name: rpilocatormon
    image: miballe/rpilocatormon
    volumes:
      - $PWD/rpimon:/log
    restart: always
    environment:
      EVENT_DELTA_MINS: "5"
      MODEL_FILTER: "RPi"
      IFTTT_ALERT_NAME: "my_alert"
      IFTTT_KEY: "ep3jdTg7T6G5yF-ihegrQq"
      FILE_TEST_MODE: "false"
      SLEEP_TIME_SECS: "300"
 
```
