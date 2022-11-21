# Twiter_Scraper
Twitter Profile Scraping Using Python 3.10 And Selenium

<h3>One click Install-<h3/>

pip install setup.py
<br>
pip install -r requirements.txt 

install_requires=
<li>python-dateutil==2.8.2<li/>
<li>selenium==4.6.0<li/>
<li>selenium-wire==4.6.4<li/>
<li>webdriver-manager==3.2.2<li/>
<li>fake-headers==1.0.2<li/>
<li>requests==2.27.1<li/>
<li>pyOpenSSL==22.0.0<li/>


<h3>Queries:<h3/>
<p style = "font-weight"= bold;>
from profile_info import scrape_profile
scrape_profile(twitter_username="bbcbangla",output_format="csv",browser="firefox",tweets_count=30,filename="bbcbangla",directory="./Output")
<p/>
          # if filename was not provided then print the JSON to console
	  # if filename was provided, save it to that file

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
