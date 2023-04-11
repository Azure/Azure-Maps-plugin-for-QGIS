import inspect
import json
import requests
import time
from urllib.parse import parse_qs, urlparse, urlencode, urlunparse

from .Constants import Constants

class AzureMapsPluginRequestHandler:
    """
    Handles the requests to Azure Maps
    Outputs formatted response
    Handles single and batch get requests
    Includes logging requests and responses
    """

    def __init__(self, subscription_key=None, geography=Constants.Geography.US, api_version=Constants.API_Versions.V20230301PREVIEW, logger=None):
        self.subscription_key = subscription_key
        self.geography = geography
        self.api_version = api_version
        self.host = Constants.Host.DEFAULT
        self.logger = logger
        
    def set_parameters(self, subscription_key=None, geography=None, api_version=None, logger=None):
        """Set parameters"""
        if subscription_key: self.set_subscription_key(subscription_key)
        if geography: self.set_geography(geography)
        if api_version: self.set_api_version(api_version)
        if logger: self.set_logger(logger)

    def set_subscription_key(self, subscription_key):
        """Set subscription key"""
        self.subscription_key = subscription_key

    def set_geography(self, geography):
        """Set geography and host"""
        self.geography = geography
        self._set_host_by_geography(geography)

    def set_host(self, host):
        """Set host"""
        self.host = host
    
    def _set_host_by_geography(self, geography):
        """Internal method to set host based on geography"""
        self.host = Constants.Host.DEFAULT
        if str(geography) == Constants.Geography.US:
            self.host = Constants.Host.US
        elif str(geography) == Constants.Geography.EU:
            self.host = Constants.Host.EU
        elif str(geography) == Constants.Geography.TEST:
            self.host = Constants.Host.US_TEST

    def set_api_version(self, api_version):
        """Set api version"""
        self.api_version = api_version

    def set_logger(self, logger):
        """Set logger"""
        self.logger = logger

    def _response_logging(self, url, request_type, resp):
        """Logs the response"""
        if self.logger:
            # Log the request
            self.logger.QLogInfo(url=url, request_type=request_type)
            if resp["success"]: # Log Success Response
                self.logger.QLogInfo(status_code=resp["response"].status_code, status_text=Constants.Logs.SUCCESS)
            else: # Log Failure Response
                if resp["response"]:
                    self.logger.QLogCrit(status_code=resp["response"].status_code, status_text=resp["error_text"], inspect_frame=inspect.currentframe())
                else:
                    self.logger.QLogCrit(status=Constants.Logs.FAILURE, status_text=resp["error_text"], inspect_frame=inspect.currentframe())

    def _format_url(self, url, query_params={}, **kwargs):
        """Formats the url with the given query parameters"""
        if not url: return None

        # Replace url parts according to the geography
        if self.geography == Constants.Geography.US:
            url = url.replace("//atlas.microsoft.com", "//us.atlas.microsoft.com")
        elif self.geography == Constants.Geography.EU:
            url = url.replace("//atlas.microsoft.com", "//eu.atlas.microsoft.com")
        elif self.geography == Constants.Geography.TEST:
            url = url.replace("//atlas.microsoft.com", "//us.t-azmaps.azurelbs.com")
        elif self.geography == Constants.Geography.LOCALHOST:
            url = url.replace("//atlas.microsoft.com", "//localhost:3000")
            url = url.replace("https", "http", 1) # Replace first instance of https with http
        
        # Add the subscription key and api version to the query parameters
        query_params["subscription-key"] = self.subscription_key
        query_params["api-version"] = self.api_version
        # Add the additional query parameters
        for key, value in kwargs.items():
            query_params[key] = value
        
        url_parts = urlparse(url) # Parse the url
        qs = dict(parse_qs(url_parts.query)) # Parse the query string
        qs.update(query_params) # Update the query string with the new query parameters. If the query parameter already exists, it will be overwritten
        url_parts = url_parts._replace(query=urlencode(qs, doseq=True)) # Replace the query string with the new query string

        return urlunparse(url_parts) # Return the formatted url

    def _get_next_link(self, response):
        """Gets the next link from the response"""
        r_json = response.json()
        links = r_json["links"]
        for link in links:
            if link["rel"] == "next":
                return link["href"]
        return None

    def make_request(self, url, request_type, body=None, content_type=None, **kwargs):
        """Makes a request to the given url""" 
        url = self._format_url(url, **kwargs) # Format the url
        error_text=None
        if(request_type == Constants.HTTPS.Methods.GET): method = requests.get
        elif(request_type == Constants.HTTPS.Methods.POST): method = requests.post
        elif(request_type == Constants.HTTPS.Methods.PUT): method = requests.put
        elif(request_type == Constants.HTTPS.Methods.DELETE): method = requests.delete
        elif(request_type == Constants.HTTPS.Methods.PATCH): method = requests.patch
        else : raise Exception("Invalid request type")
        headers = {"content-type": content_type} if content_type else {} # Set the headers
        verify_ssl = False if self.geography == Constants.Geography.LOCALHOST else True

        retry, retry_counter = True, 0

        while retry:
            try:
                r = method(url, data=body, headers=headers, timeout=60, verify=verify_ssl) # Make the request
            except requests.exceptions.Timeout as err:
                error_text = "Timeout occurred while sending {} request. Error: {}".format(request_type, str(err))
            except requests.exceptions.ConnectionError as err:
                error_text = "Connection error occurred while sending {} request. Error: {}".format(request_type, str(err))
            except requests.exceptions.RequestException as err:
                error_text = "Exception occurred while sending {} request. Error: {}".format(request_type, str(err))
            except Exception as err:
                error_text = "Unexpected exception occurred while sending {} request. Error: {}".format(request_type, str(err))
            
            retry = False # No need to retry, except in case of error
            if error_text: # Error occurred before the request was made
                resp = {
                    "success": False,
                    "error_text": error_text,
                    "response": None
                }
            elif r.status_code < 200 or r.status_code >= 300: # Error status codes
                if not r.text:
                    error_text = "Error occurred while sending {} request.".format(request_type)
                else:
                    error_text = r.json()["error"]["message"]
                    
                resp = {
                    "success": False,
                    "error_text": error_text,
                    "response": r
                }
                if retry_counter < Constants.HTTPS.MAX_RETRIES:
                    retry = True # Retry
                    retry_counter += 1
                    time.sleep(retry_counter * Constants.HTTPS.RETRY_INTERVAL) # Wait before retrying
                    self._response_logging(url=url, request_type=request_type, resp=resp) # Log the response
                    self.logger.QLogCrit(status=Constants.Logs.FAILURE, 
                                         status_text="API called failed. Attempt {}. Retrying...".format(retry_counter)) # Log the retry
            else: # Success!
                resp = {
                    "success": True,
                    "error_text": None,
                    "response": r
                }
        # Log the response/error
        self._response_logging(url=url, request_type=request_type, resp=resp)
        return resp
    
    def get_request(self, url, limit=Constants.HTTPS.GET_LIMIT, single_request=False, **kwargs):
        """Makes a get request to the given url"""
        returnDict = {"success": True, "error_text": None, "response": {}} # Return dict with empty response

        # Loop until there is no next link, or until an error occurs
        while url:
            resp = self.make_request(url, Constants.HTTPS.Methods.GET, limit=limit, **kwargs) # Pass on limit and other query parameters
            if not resp["success"]:
                return resp # Error is captured as error_text in the return value
            
            if not returnDict["response"]:
                returnDict["response"] = resp["response"].json() # First response
            else:
                returnDict["response"]["features"].extend(resp["response"].json()["features"]) # Append features for successive responses
            
            if single_request: break # If single request, break after first response
            next_link = self._get_next_link(resp["response"]) # Get next link
            url = self._format_url(next_link, query_params={"limit": limit}) # Update url for next request
        return returnDict
    
    def get_request_parallel(self, task, _id, request_type, url, limit, **kwargs):
        """
        Makes a get request to the given url in parallel
        Task needs to be the first parameter in the function, as specified by the QGSTask class
        _id and request_type are used for logging and displaying user responses
        """
        return self.get_request(url, limit, **kwargs) # Call the get_request function

    def post_request(self, url, body=None, content_type=None, **kwargs):
        """Makes a post request to the given url"""
        if not content_type: content_type = Constants.HTTPS.Content_type.GEOJSON
        return self.make_request(url, Constants.HTTPS.Methods.POST, body, content_type, **kwargs)

    def put_request(self, url, body=None, content_type=None, **kwargs):
        """Makes a put request to the given url"""
        if not content_type: content_type = Constants.HTTPS.Content_type.GEOJSON
        return self.make_request(url, Constants.HTTPS.Methods.PUT, body, content_type, **kwargs)
    
    def delete_request(self, url, **kwargs):
        """Makes a delete request to the given url"""
        return self.make_request(url, Constants.HTTPS.Methods.DELETE, **kwargs)

    def patch_request(self, url, body=None, content_type=None, **kwargs):
        """Makes a patch request to the given url"""
        if not content_type: content_type = Constants.HTTPS.Content_type.PATCH_JSON
        return self.make_request(url, Constants.HTTPS.Methods.PATCH, body, content_type, **kwargs)
