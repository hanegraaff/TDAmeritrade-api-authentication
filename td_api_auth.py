'''
    td_api_auth.py
        A sample script to test out the TDAmeritrade OAUth2 login process
        and API usage.

        Note that the authorization process is manual and must be repeated every
        three months. It shoul be possible to automate this as well

    Author: Mark Hanegraaff


    For detained instruction on how to authorize an App with TDAmeritrade and
    get a refresh token that will last 3 months, see the readme from this project.

    https://github.com/hanegraaff/TDAmeritrade-api-authentication/

    TLDR;

    Original documentation:

    https://developer.tdameritrade.com/content/phase-1-authentication-update-xml-based-api
    https://developer.tdameritrade.com/content/simple-auth-local-apps

    1) Create and account with https://developer.tdameritrade.com
    
    2) Regsiter a New App: 
        a. Set the callback URL to: https://127.0.0.1
        b. Note the "Consumer Key" This is also referred to "Client ID"
    
    3) Get the the authorization code from TDAmeritrade by going to this URL:

        https://auth.tdameritrade.com/auth?response_type=code&redirect_uri={URLENCODED REDIRECT URI}&client_id={URLENCODED Consumer Key}%40AMER.OAUTHAP

        For example:

        https://auth.tdameritrade.com/auth?response_type=code&redirect_uri=https%3A%2F%2F127.0.0.1&client_id=MYCONSUMERKEY%40AMER.OAUTHAP

    4) The redirect will fail but note the authorization code that is returned in the URL.

    5) Use the authorization code and use it here here:
        https://developer.tdameritrade.com/authentication/apis/post/token-0

        -----------------------------------------------------
        grant_type: authorization_code
        access_type: offline
        code: {The Authorization code from the previous step}
        client_id: {Consumer Key} (e.g. EXAMPLE@AMER.OAUTHAP)
        redirect_uri: {REDIRECT URI} (e.g. https://127.0.0.1)
        -----------------------------------------------------

        This will return a refresh token that will be valid for 3 months,
        after which you must repeat the process.
'''

import requests
import json
import logging
import argparse


logging.basicConfig(level=logging.INFO, format='[%(levelname)s] - %(message)s')

# uncomment this to see debug level statements in the 'requests' package
#logging.basicConfig(level=logging.DEBUG)

log = logging.getLogger()

def parse_params():
    """
        Parse command line parameters
        
        Returns
        ----------
        A String containing the mode (encode/decode) of the app
        
    """

    description = """ A Demonstraton of the TDAmeritrade APIs, Specifically this shows
                how to generate an access code and use it to call an API
              """

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("-client_id", help="The Client ID (Consumer Key) of the registed application", type=str, required=True)
    parser.add_argument("-refresh_token", help="The Refresh Token generated using the login process", type=str, required=True)
    parser.add_argument("-account_id", help="The TDAmeritrade brokerage account ID", type=str, required=True)


    args = parser.parse_args()

    client_id = args.client_id
    refresh_token = args.refresh_token
    td_account_id = args.account_id

    return (client_id, refresh_token, td_account_id)



(client_id, refresh_token, td_account_id) = parse_params()


# Step 1 - get the the temp access token (valid for 30 min)
r = requests.post('https://api.tdameritrade.com/v1/oauth2/token', data = 
    {
        'grant_type' : 'refresh_token',
        'refresh_token' : refresh_token,
        'client_id' : '%s@AMER.OAUTHAP' % client_id
    }
)
if (r.status_code not in (200, 201)):
    log.error("Unable to generate refresh token")
    log.error(r.text)
else:
    # Use the access token to call an API
    json_data = json.loads(r.text)

    access_token = json_data['access_token']

    log.info("Generated Access Token")

    # interact with TDAmeritrade using the API Directly
    params = {'fields': ['positions']}
    r = requests.get('https://api.tdameritrade.com/v1/accounts/%s' % td_account_id, params=params, headers={'Authorization' : 'Bearer %s' % access_token} )
    
    if (r.status_code not in (200, 201)):
        log.error("Unable to show order details")
        log.error(r.text)
    else:
        log.info("Displaying Account Info")
        log.info(json.dumps(json.loads(r.text), indent=4))
