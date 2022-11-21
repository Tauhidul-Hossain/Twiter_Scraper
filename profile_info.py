import re
import json
import requests
import time
import csv
import os
import logging
from fake_headers import Headers
from seleniumwire import webdriver
from selenium.webdriver.edge.options import Options as CustomEdgeOptions
from selenium.webdriver.chrome.options import Options as CustomChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.firefox.options import Options as CustomFireFoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from random import randint
from dateutil.parser import parse
from urllib.parse import quote
from typing import Union



logger = logging.getLogger(__name__)
format = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s")
ch = logging.StreamHandler()
ch.setFormatter(format)
logger.addHandler(ch)

class Initializer:
    def __init__(self, browser_name: str, headless: bool, proxy: Union[str, None] = None, profile: Union[str, None] = None):
        """Initialize Browser

        Args:
            browser_name (str): Browser Name
            headless (bool): Whether to run Browser in headless mode?
            proxy (Union[str, None], optional): Optional parameter, if user wants to use proxy for scraping. If the proxy is authenticated proxy then the proxy format is username:password@host:port. Defaults to None.
            profile (Union[str, None], optional): Path of Browser Profile where cookies might be located to scrap data in authenticated way. Defaults to None.
      """
        self.browser_name = browser_name
        self.proxy = proxy
        self.headless = headless
        self.profile = profile

    def set_properties(self, browser_option):
        """adds capabilities to the driver"""
        header = Headers().generate()['User-Agent']
        if self.headless:
            # runs browser in headless mode
            browser_option.add_argument("--headless")
        if self.profile and self.browser_name.lower() == "chrome":
            browser_option.add_argument(
                "user-data-dir={}".format(self.profile))
        if self.profile and self.browser_name.lower() == "edge":
            logger.setLevel(logging.INFO)
            logger.info("Using Proxy: {}".format(self.proxy))
            browser_option.add_argument("-profile")
            browser_option.add_argument(
                "user-data-dir={}".format(self.profile))
        if self.profile and self.browser_name.lower() == "firefox":
            logger.setLevel(logging.INFO)
            logger.info("Loading Profile from {}".format(self.profile))
            browser_option.add_argument("-profile")
            browser_option.add_argument(self.profile)
        browser_option.add_argument('--no-sandbox')
        browser_option.add_argument("--disable-dev-shm-usage")
        browser_option.add_argument('--ignore-certificate-errors')
        browser_option.add_argument('--disable-gpu')
        browser_option.add_argument('--log-level=3')
        browser_option.add_argument('--disable-notifications')
        browser_option.add_argument('--disable-popup-blocking')
        browser_option.add_argument('--user-agent={}'.format(header))
        return browser_option

    def set_driver_for_browser(self, browser_name: str):
        """expects browser name and returns a driver instance"""
        # if browser is suppose to be chrome
        if browser_name.lower() == "chrome":
            browser_option = CustomChromeOptions()
            # automatically installs chromedriver and initialize it and returns the instance
            if self.proxy is not None:
                options = {
                    'https': 'https://{}'.format(self.proxy.replace(" ", "")),
                    'http': 'http://{}'.format(self.proxy.replace(" ", "")),
                    'no_proxy': 'localhost, 127.0.0.1'
                }
                logger.setLevel(logging.INFO)
                logger.info("Using Proxy: {}".format(self.proxy))

                return webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),
                                        options=self.set_properties(browser_option), seleniumwire_options=options)

            return webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=self.set_properties(browser_option))
        elif browser_name.lower() == "firefox":
            browser_option = CustomFireFoxOptions()
            if self.proxy is not None:
                options = {
                    'https': 'https://{}'.format(self.proxy.replace(" ", "")),
                    'http': 'http://{}'.format(self.proxy.replace(" ", "")),
                    'no_proxy': 'localhost, 127.0.0.1'
                }
                logger.setLevel(logging.INFO)
                logger.info("Using Proxy: {}".format(self.proxy))
                return webdriver.Firefox(service=FirefoxService(executable_path=GeckoDriverManager().install()),
                                         options=self.set_properties(browser_option), seleniumwire_options=options)

            # automatically installs geckodriver and initialize it and returns the instance
            return webdriver.Firefox(service=FirefoxService(executable_path=GeckoDriverManager().install()), options=self.set_properties(browser_option))
        elif browser_name.lower() == "edge":
            browser_option = CustomEdgeOptions()
            if self.proxy is not None:
                options = {
                    'https': 'https://{}'.format(self.proxy.replace(" ", "")),
                    'http': 'http://{}'.format(self.proxy.replace(" ", "")),
                    'no_proxy': 'localhost, 127.0.0.1'
                }
                logger.setLevel(logging.INFO)
                logger.info("Using Proxy: {}".format(self.proxy))
                return webdriver.Edge(service=EdgeService(executable_path=EdgeChromiumDriverManager().install()), options=self.set_properties(browser_option), seleniumwire_options=options)
                # automatically installs msedgedriver and initialize it and returns the instance
            return webdriver.Edge(service=EdgeService(executable_path=EdgeChromiumDriverManager().install()), options=self.set_properties(browser_option))
        else:
            # if browser_name is not chrome neither firefox than raise an exception
            raise Exception("Browser not supported!")

    def init(self):
        """returns driver instance"""
        driver = self.set_driver_for_browser(self.browser_name)
        return driver



class Scraping_utilities:
    """
    This class contains all utility methods that help cleaning or extracting
    data from raw data.

    @staticmethod
    def method_name(parameters)
    """

    @staticmethod
    def parse_name(string) -> Union[str, None]:
        """Extract name from the given string.
           Example:
           Input: jack(@jack)
           Output: jack
        """
        try:
            return string.split("(")[0].strip()
        except Exception as ex:
            logger.exception("Error at parse_name : {}".format(ex))

    @staticmethod
    def extract_digits(string) -> Union[int, None]:
        """Extracts first digits from the string.

        Args:
          string (str): string containing digits.

        Returns:
          int: digit that was extracted from the passed string
        """
        try:
            return int(re.search(r'\d+', string).group(0)) # type: ignore
        except Exception as ex:
            logger.exception("Error at extract_digits : {}".format(ex))

    @staticmethod
    def set_value_or_none(value, string) -> Union[str, None]:
        return string+str(value)+" " if value is not None else None

    @staticmethod
    def url_generator(keyword: str, since: Union[int, None] = None, until: Union[str, None] = None,
                      since_id: Union[int, None] = None, max_id: Union[int, None] = None,
                      within_time: Union[str, None] = None) -> str:
        """Generates Twitter URL for passed keyword

        Args:
            keyword (str): Keyword to search on twitter.
            since (Union[int, None], optional): Optional parameter,Since date for scraping,a past date from where to search from. Format for date is YYYY-MM-DD or unix timestamp in seconds. Defaults to None.
            until (Union[str, None], optional): Optional parameter,Until date for scraping,a end date from where search ends. Format for date is YYYY-MM-DD or unix timestamp in seconds. Defaults to None.
            since_id (Union[int, None], optional): After (NOT inclusive) a specified Snowflake ID. Defaults to None.
            max_id (Union[int, None], optional): At or before (inclusive) a specified Snowflake ID. Defaults to None.
            within_time (Union[str, None], optional): Search within the last number of days, hours, minutes, or seconds. Defaults to None.

        Returns:
            str: Twitter URL
        """
        base_url = "https://twitter.com/search?q="
        if within_time is None:
            words = [Scraping_utilities.set_value_or_none(since, "since:"),
                     Scraping_utilities.set_value_or_none(
                until, "until:"),
                Scraping_utilities.set_value_or_none(
                since_id, "since_id:"), Scraping_utilities.set_value_or_none(max_id, "max_id:")]
            query = ""
            for word in words:
                if word is not None:
                    query += word
            query += keyword
            query = quote(query)
            base_url = base_url + query + "&src=typed_query&f=live"
        else:
            word = Scraping_utilities.set_value_or_none(
                within_time, "within_time:")
            query = keyword + " " + word  # type: ignore
            base_url = base_url + quote(query) + "&src=typed_query&f=live"
        return base_url

    @staticmethod
    def make_http_request_with_params(URL, params, headers, proxy=None):
        try:
            response = None
            if proxy:
                proxy_dict = {
                    "http": "http://{}".format(proxy),
                    "https": "http://{}".format(proxy)
                }
                response = requests.get(URL, params=params, headers=headers,
                                        proxies=proxy_dict)
            else:
                response = requests.get(URL, params=params, headers=headers)
            if response and response.status_code == 200:
                return response.json()
        except Exception as ex:
            logger.warning("Error at make_http_request: {}".format(ex))

    @staticmethod
    def make_http_request(URL, headers, proxy=None):
        try:
            response = None
            if proxy:
                proxy_dict = {
                    "http": "http://{}".format(proxy),
                    "https": "http://{}".format(proxy)
                }
                response = requests.get(URL, headers=headers,
                                        proxies=proxy_dict)
            else:
                response = requests.get(URL, headers=headers)
            if response and response.status_code == 200:
                return response.json()
        except Exception as ex:
            logger.warning("Error at make_http_request: {}".format(ex))

    @staticmethod
    def build_params(query, cursor=None):
        params = {
            'include_profile_interstitial_type': '1',
            'include_blocking': '1',
            'include_blocked_by': '1',
            'include_followed_by': '1',
            'include_want_retweets': '1',
            'include_mute_edge': '1',
            'include_can_dm': '1',
            'include_can_media_tag': '1',
            'include_ext_has_nft_avatar': '1',
            'skip_status': '1',
            'cards_platform': 'Web-12',
            'include_cards': '1',
            'include_ext_alt_text': 'true',
            'include_ext_limited_action_results': 'false',
            'include_quote_count': 'true',
            'include_reply_count': '1',
            'tweet_mode': 'extended',
            'include_ext_collab_control': 'true',
            'include_entities': 'true',
            'include_user_entities': 'true',
            'include_ext_media_color': 'true',
            'include_ext_media_availability': 'true',
            'include_ext_sensitive_media_warning': 'true',
            'include_ext_trusted_friends_metadata': 'true',
            'send_error_codes': 'true',
            'simple_quoted_tweet': 'true',
            'q': query,
            'vertical': 'trends',
            'count': '20',
            'query_source': 'trend_click',
            'pc': '1',
            'spelling_corrections': '1',
            'include_ext_edit_control': 'true',
            'ext': 'mediaStats,highlightedLabel,hasNftAvatar,voiceInfo,enrichments,superFollowMetadata,unmentionInfo,editControl,collab_control,vibe',
        }
        if cursor:
            params['cursor'] = cursor
        return params

    @staticmethod
    def build_keyword_headers(x_guest_token, authorization_key, query=None):
        headers = {
            'authority': 'twitter.com',
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'authorization': authorization_key,
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': Headers().generate()['User-Agent'],
            'x-guest-token': x_guest_token,
            'x-twitter-active-user': 'yes',
            'x-twitter-client-language': 'en',
        }
        if query:
            headers['referer'] = "https://twitter.com/search?q={}".format(
                query)
        return headers

    @staticmethod
    def build_topic_headers(x_guest_token, authorization_key, rest_id=None):
        headers = {
            'authority': 'twitter.com',
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'authorization': authorization_key,
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': Headers().generate()['User-Agent'],
            'x-guest-token': x_guest_token,
            'x-twitter-active-user': 'yes',
            'x-twitter-client-language': 'en',
        }
        if rest_id:
            headers['referer'] = "https://twitter.com/i/topics/{}".format(
                rest_id)
        return headers

    @staticmethod
    def find_x_guest_token(authorization_key, proxy=None):
        try:
            headers = {
                'authorization': authorization_key,
            }
            response = None
            if proxy:
                proxy_dict = {
                    "http": "http://{}".format(proxy),
                    "https": "http://{}".format(proxy),
                }
                response = requests.post(
                    'https://api.twitter.com/1.1/guest/activate.json', headers=headers, proxies=proxy_dict)  # type: ignore
                return response.json()['guest_token']

            response = requests.post(
                'https://api.twitter.com/1.1/guest/activate.json', headers=headers)
            return response.json()['guest_token']
        except Exception as ex:
            logger.warning("Error at find_x_guest_token: {}".format(ex))

    @staticmethod
    def build_topic_params(rest_id, cursor):
        variables = {"rest_id": rest_id, "context": "{}", "withSuperFollowsUserFields": True, "withDownvotePerspective": False,
                     "withReactionsMetadata": False, "withReactionsPerspective": False, "withSuperFollowsTweetFields": True}
        if cursor:
            variables["cursor"] = cursor
        params = {
            'variables': json.dumps(variables),
            'features': '{"verified_phone_label_enabled":false,"responsive_web_graphql_timeline_navigation_enabled":true,"unified_cards_ad_metadata_container_dynamic_card_content_query_enabled":true,"tweetypie_unmention_optimization_enabled":true,"responsive_web_uc_gql_enabled":true,"vibe_api_enabled":true,"responsive_web_edit_tweet_api_enabled":true,"graphql_is_translatable_rweb_tweet_is_translatable_enabled":true,"standardized_nudges_misinfo":true,"tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled":false,"interactive_text_enabled":true,"responsive_web_text_conversations_enabled":false,"responsive_web_enhance_cards_enabled":true}',
        }
        return params


#################################
class Utilities:
    """
    this class contains all the method related to driver behaviour,
    like scrolling, waiting for element to appear, it contains all static
    method, which accepts driver instance as a argument

    @staticmethod
    def method_name(parameters):
    """

    @staticmethod
    def wait_until_tweets_appear(driver) -> None:
        """Wait for tweet to appear. Helpful to work with the system facing
        slow internet connection issues
        """
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, '[data-testid="tweet"]')))
        except WebDriverException:
            logger.exception(
                "Tweets did not appear!, Try setting headless=False to see what is happening")

    @staticmethod
    def scroll_down(driver) -> None:
        """Helps to scroll down web page"""
        try:
            body = driver.find_element(By.CSS_SELECTOR, 'body')
            for _ in range(randint(1, 3)):
                body.send_keys(Keys.PAGE_DOWN)
        except Exception as ex:
            logger.exception("Error at scroll_down method {}".format(ex))

    @staticmethod
    def wait_until_completion(driver) -> None:
        """waits until the page have completed loading"""
        try:
            state = ""
            while state != "complete":
                time.sleep(randint(3, 5))
                state = driver.execute_script("return document.readyState")
        except Exception as ex:
            logger.exception('Error at wait_until_completion: {}'.format(ex))

#######################################

class Finder:
    """
    this class should contain all the static method to find that accept
    webdriver instance and perform operation to find elements and return the
    found element.
    method should follow convention like so:

    @staticmethod
    def method_name(parameters):
    """

    @staticmethod
    def find_all_tweets(driver) -> list:
        """finds all tweets from the page"""
        try:
            return driver.find_elements(By.CSS_SELECTOR, '[data-testid="tweet"]')
        except Exception as ex:
            logger.exception(
                "Error at method fetch_all_tweets : {}".format(ex))
            return []

    @staticmethod
    def find_replies(tweet) -> Union[int, str]:
        """finds replies from the tweet"""
        try:
            replies_element = tweet.find_element(
                By.CSS_SELECTOR, '[data-testid="reply"]')
            replies = replies_element.get_attribute("aria-label")
            return Scraping_utilities.extract_digits(replies)  # type: ignore
        except Exception as ex:
            logger.exception("Error at method find_replies : {}".format(ex))
            return ""

    @staticmethod
    def find_shares(tweet) -> Union[int, str]:
        """finds shares from the tweet"""
        try:
            shares_element = tweet.find_element(
                By.CSS_SELECTOR, '[data-testid="retweet"]')
            shares = shares_element.get_attribute("aria-label")
            return Scraping_utilities.extract_digits(shares)  # type: ignore
        except Exception as ex:
            logger.exception("Error at method find_shares : {}".format(ex))
            return ""

    @staticmethod
    def find_status(tweet) -> Union[list, tuple]:
        """finds status and link from the tweet"""
        try:
            anchor = tweet.find_element(
                By.CSS_SELECTOR, "a[aria-label][dir]")
            return (anchor.get_attribute("href").split("/"), anchor.get_attribute("href"))
        except Exception as ex:
            logger.exception("Error at method find_status : {}".format(ex))
            return []

    @staticmethod
    def find_all_anchor_tags(tweet) -> Union[list, None]:
        """finds all anchor tags from the tweet"""
        try:
            return tweet.find_elements(By.TAG_NAME, 'a')
        except Exception as ex:
            logger.exception(
                "Error at method find_all_anchor_tags : {}".format(ex))

    @staticmethod
    def find_timestamp(tweet) -> Union[str, None]:
        """finds timestamp from the tweet"""
        try:
            timestamp = tweet.find_element(By.TAG_NAME,
                                           "time").get_attribute("datetime")
            posted_time = parse(timestamp).isoformat()
            return posted_time
        except Exception as ex:
            logger.exception("Error at method find_timestamp : {}".format(ex))

    @staticmethod
    def find_content(tweet) -> Union[str, None]:
        try:
            #content_element = tweet.find_element('.//*[@dir="auto"]')[4]
            content_element = tweet.find_element(By.CSS_SELECTOR, 'div[lang]')
            return content_element.text
        except NoSuchElementException:
            return ""
        except Exception as ex:
            logger.exception("Error at method find_content : {}".format(ex))

    @staticmethod
    def find_like(tweet) -> Union[int, None]:
        """finds the like of the tweet"""
        try:
            like_element = tweet.find_element(
                By.CSS_SELECTOR, '[data-testid="like"]')
            likes = like_element.get_attribute("aria-label")
            return Scraping_utilities.extract_digits(likes)
        except Exception as ex:
            logger.exception("Error at method find_like : {}".format(ex))

    @staticmethod
    def find_images(tweet) -> Union[list, None]:
        """finds all images of the tweet"""
        try:
            image_element = tweet.find_elements(By.CSS_SELECTOR,
                                                'div[data-testid="tweetPhoto"]')
            images = []
            for image_div in image_element:
                href = image_div.find_element(By.TAG_NAME,
                                              "img").get_attribute("src")
                images.append(href)
            return images
        except Exception as ex:
            logger.exception("Error at method find_images : {}".format(ex))
            return []

    @staticmethod
    def find_videos(tweet) -> list:
        """finds all videos present in the tweet"""
        try:
            image_element = tweet.find_elements(By.CSS_SELECTOR,
                                                'div[data-testid="videoPlayer"]')
            videos = []
            for video_div in image_element:
                href = video_div.find_element(
                    By.TAG_NAME, "video").get_attribute("src")
                videos.append(href)
            return videos
        except Exception as ex:
            logger.exception("Error at method find_videos : {}".format(ex))
            return []

    @staticmethod
    def is_retweet(tweet) -> bool:
        """return if the tweet is whether re-tweet"""
        try:
            tweet.find_element(By.CSS_SELECTOR, 'div.r-92ng3h.r-qvutc0')
            return True
        except NoSuchElementException:
            return False
        except Exception as ex:
            logger.exception("Error at method is_retweet : {}".format(ex))
            return False

    @staticmethod
    def find_name_from_tweet(tweet, is_retweet=False) -> Union[str, None]:
        """finds the name from the post"""
        try:
            name = "NA"
            anchors = Finder.find_all_anchor_tags(tweet)
            if len(anchors) > 2:  # type: ignore
                if is_retweet:
                    name = tweet.find_element(
                        By.CSS_SELECTOR, '[data-testid="User-Names"] > div a').text
                else:
                    name = anchors[1].text.split("\n")[0] # type: ignore
            return name
        except Exception as ex:
            logger.exception(
                "Error at method find_name_from_post : {}".format(ex))

    @staticmethod
    def find_external_link(tweet) -> Union[str, None]:
        """finds external link from the tweet"""
        try:
            card = tweet.find_element(
                By.CSS_SELECTOR, '[data-testid="card.wrapper"]')
            href = card.find_element(By.TAG_NAME, 'a')
            return href.get_attribute("href")

        except NoSuchElementException:
            return ""
        except Exception as ex:
            logger.exception(
                "Error at method find_external_link : {}".format(ex))

    @staticmethod
    def find_profile_image_link(tweet) -> Union[str, None]:
        """finds profile image links

        Args:
            tweet: Tweet Element

        Returns:
            Union[str, None]: returns string containing image link.
        """
        try:
            return tweet.find_element(By.CSS_SELECTOR, 'img[alt][draggable="true"]').get_attribute('src')
        except Exception as ex:
            logger.warning("Error at find_profile_image_link : {}".format(ex))

    @staticmethod
    def find_graphql_key(driver, URL):
      try:
        driver.get(URL)
        Utilities.wait_until_completion(driver)
        URL = None
        for request in driver.requests:
          if 'TopicLandingPage' in request.url:
            URL = request.url
            break
        if not URL:
          logger.exception('Failed to find key!')
        logger.debug('Key Found!')
        return URL.split('/')[6] # type: ignore
      except Exception as ex:
        logger.warning('Error at find_graphql_link : {}'.format(ex))

class Profile:
    """this class needs to be instantiated in order to scrape post of some
    twitter profile"""

    def __init__(self, twitter_username, browser, proxy, tweets_count, headless, browser_profile):
        self.twitter_username = twitter_username
        self.URL = "https://twitter.com/{}".format(twitter_username.lower())
        self.__driver = ""
        self.browser = browser
        self.proxy = proxy
        self.tweets_count = tweets_count
        self.posts_data = {}
        self.retry = 20
        self.headless = headless
        self.browser_profile = browser_profile

    def __start_driver(self):
        """changes the class member __driver value to driver on call"""
        self.__driver = Initializer(
            self.browser, self.headless, self.proxy, self.browser_profile).init()

    def __close_driver(self):
        self.__driver.close()  # type: ignore
        self.__driver.quit() # type: ignore

    def __check_tweets_presence(self, tweet_list):
        if len(tweet_list) <= 0:
            self.retry -= 1

    def __check_retry(self):
        return self.retry <= 0

    def __fetch_and_store_data(self):
        try:
            all_ready_fetched_posts = []
            present_tweets = Finder.find_all_tweets(self.__driver)
            self.__check_tweets_presence(present_tweets)
            all_ready_fetched_posts.extend(present_tweets)

            while len(self.posts_data) < self.tweets_count:
                for tweet in present_tweets:
                    status, tweet_url = Finder.find_status(tweet)
                    replies = Finder.find_replies(tweet)
                    retweets = Finder.find_shares(tweet)
                    status = status[-1]
                    username = tweet_url.split("/")[3]
                    is_retweet = True if self.twitter_username.lower() != username.lower() else False
                    name = Finder.find_name_from_tweet(
                        tweet, is_retweet)
                    retweet_link = tweet_url if is_retweet is True else ""
                    posted_time = Finder.find_timestamp(tweet)
                    content = Finder.find_content(tweet)
                    likes = Finder.find_like(tweet)
                    images = Finder.find_images(tweet)
                    videos = Finder.find_videos(tweet)
                    hashtags = re.findall(r"#(\w+)", content) # type: ignore
                    mentions = re.findall(r"@(\w+)", content) # type: ignore
                    profile_picture = Finder.find_profile_image_link(tweet)
                    link = Finder.find_external_link(tweet)
                    self.posts_data[status] = {
                        "tweet_id": status,
                        "username": username,
                        "name": name,
                        "profile_picture": profile_picture,
                        "replies": replies,
                        "retweets": retweets,
                        "likes": likes,
                        "is_retweet": is_retweet,
                        "retweet_link": retweet_link,
                        "posted_time": posted_time,
                        "content": content,
                        "hashtags": hashtags,
                        "mentions": mentions,
                        "images": images,
                        "videos": videos,
                        "tweet_url": tweet_url,
                        "link": link
                    }

                Utilities.scroll_down(self.__driver)
                Utilities.wait_until_completion(self.__driver)
                Utilities.wait_until_tweets_appear(self.__driver)
                present_tweets = Finder.find_all_tweets(
                    self.__driver)
                present_tweets = [
                    post for post in present_tweets if post not in all_ready_fetched_posts]
                self.__check_tweets_presence(present_tweets)
                all_ready_fetched_posts.extend(present_tweets)
                if self.__check_retry() is True:
                    break

        except Exception as ex:
            logger.exception(
                "Error at method fetch_and_store_data : {}".format(ex))

    def scrap(self):
        try:
            self.__start_driver()
            self.__driver.get(self.URL) # type: ignore
            Utilities.wait_until_completion(self.__driver)
            Utilities.wait_until_tweets_appear(self.__driver)
            self.__fetch_and_store_data()
            self.__close_driver()
            data = dict(list(self.posts_data.items())
                        [0:int(self.tweets_count)])
            return data
        except Exception as ex:
            self.__close_driver()
            logger.exception(
                "Error at method scrap : {} ".format(ex))


def json_to_csv(filename, json_data, directory):
    os.chdir(directory)  # change working directory to given directory
    # headers of the CSV file
    fieldnames = ['tweet_id', 'username', 'name', 'profile_picture', 'replies',
                  'retweets', 'likes', 'is_retweet', 'retweet_link', 'posted_time', 'content', 'hashtags', 'mentions',
                  'images', 'videos', 'tweet_url', 'link']
    mode = 'w'
    if os.path.exists("{}.csv".format(filename)):
        mode = 'a'
    # open and start writing to CSV files
    with open("{}.csv".format(filename), mode, newline='', encoding="utf-8") as data_file:
        # instantiate DictWriter for writing CSV fi
        writer = csv.DictWriter(data_file, fieldnames=fieldnames)
        if mode == 'w':
            writer.writeheader()  # write headers to CSV file
        # iterate over entire dictionary, write each posts as a row to CSV file
        for key in json_data:
            # parse post in a dictionary and write it as a single row
            row = {
                "tweet_id": key,
                "username": json_data[key]['username'],
                "name": json_data[key]['name'],
                "profile_picture": json_data[key]['profile_picture'],
                "replies": json_data[key]['replies'],
                "retweets": json_data[key]['retweets'],
                "likes": json_data[key]['likes'],
                "is_retweet": json_data[key]['is_retweet'],
                "retweet_link": json_data[key]['retweet_link'],
                "posted_time": json_data[key]['posted_time'],
                "content": json_data[key]['content'],
                "hashtags": json_data[key]['hashtags'],
                "mentions": json_data[key]['mentions'],
                "images": json_data[key]['images'],
                "videos": json_data[key]['videos'],
                "tweet_url": json_data[key]['tweet_url'],
                "link": json_data[key]['link']
            }
            writer.writerow(row)  # write row to CSV file
        data_file.close()  # after writing close the file
    logger.setLevel(logging.INFO)
    logger.info('Data Successfully Saved to {}.csv'.format(filename))


def scrape_profile(twitter_username: str, browser: str = "firefox", proxy: Union[str, None] = None,
                  tweets_count: int = 30, output_format: str = "json", filename: str = "", directory: str = os.getcwd(),
                  headless: bool = True, browser_profile: Union[str, None] = None):
    """Scrap tweets of twitter profile using twitter username.

    Args:
        twitter_username (str): Twitter username of the account.
        browser (str, optional): Which browser to use for scraping?, Only 2 are supported Chrome and Firefox. Defaults to "firefox".
        proxy (Union[str, None], optional): Optional parameter, if user wants to use proxy for scraping. If the proxy is authenticated proxy then the proxy format is username:password@host:port. Defaults to None.
        tweets_count (int, optional): Number of posts to scrap. Defaults to 10.
        output_format (str, optional): The output format, whether JSON or CSV. Defaults to "json".
        filename (str, optional): If output_format parameter is set to CSV, then it is necessary for filename parameter to passed. If not passed then the filename will be same as keyword passed. Defaults to "".
        directory (str, optional): If output_format parameter is set to CSV, then it is valid for directory parameter to be passed. If not passed then CSV file will be saved in current working directory. Defaults to os.getcwd().
        headless (bool, optional): Whether to run browser in headless mode?. Defaults to True.
        browser_profile (Union[str, None], optional): Path of Browser Profile where cookies might be located to scrap data in authenticated way. Defaults to None.

    Returns:
        str: tweets data in CSV or JSON
    """
    profile_bot = Profile(twitter_username, browser,
                          proxy, tweets_count, headless, browser_profile)
    data = profile_bot.scrap()
    
    json_object = json.dumps(data, ensure_ascii=False, indent=4)
    with open("DATA.json", "w", encoding='utf-8') as outfile:
        outfile.write(json_object)
        # Writing to sample.json
    if output_format.lower() == "json":
        if filename == '':
          # if filename was not provided then print the JSON to console
            return json.dumps(data)
        elif filename != '':
          # if filename was provided, save it to that file
            mode = 'w'
            json_file_location = os.path.join(directory, filename+".json")
            if os.path.exists(json_file_location):
                mode = 'r'
            with open(json_file_location, mode, encoding='utf-8') as file:
                if mode == 'r':
                    try:
                        file_content = file.read()
                        content = json.loads(file_content)
                    except json.decoder.JSONDecodeError:
                        logger.warning('Invalid JSON Detected!')
                        content = {}
                    file.close()
                    data.update(content)  # type: ignore
                    with open(json_file_location, 'w', encoding='utf-8') as file_in_write_mode:
                        json.dump(data, file_in_write_mode)
                    with open(filename+".json", "w", encoding='utf-8') as outfile:
                        outfile.write(data)  # type: ignore
                logger.setLevel(logging.INFO)
                logger.info(
                    'Data Successfully Saved to {}'.format(json_file_location))     
    elif output_format.lower() == "csv":
        if filename == "":
            filename = twitter_username
        json_to_csv(filename=filename, json_data=data, directory=directory)