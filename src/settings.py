# Scrapy settings for grabber project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "src"

SPIDER_MODULES = ["src.spiders"]
NEWSPIDER_MODULE = "src.spiders"


DOWNLOADER_MIDDLEWARES = {
    "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware": None,
    "scrapy.downloadermiddlewares.retry.RetryMiddleware": None,
    # Values set according to
    # https://github.com/alecxe/scrapy-fake-useragent/issues/36#issuecomment-1491458670
    "scrapy_fake_useragent.middleware.RandomUserAgentMiddleware": 501,
    # This lib has not been updated since September 2023
    # And has an error with `RETRY_EXCEPTIONS`` when handling exceptions
    # Issue: https://github.com/alecxe/scrapy-fake-useragent/issues/41
    # PR: https://github.com/alecxe/scrapy-fake-useragent/pull/42
    "scrapy_fake_useragent.middleware.RetryUserAgentMiddleware": 551,
}
FAKEUSERAGENT_PROVIDERS = [
    "scrapy_fake_useragent.providers.FakeUserAgentProvider",  # this is the first provider we'll try
    "scrapy_fake_useragent.providers.FixedUserAgentProvider",  # fall back to USER_AGENT value
]
# Set the FAKEUSERAGENT_FALLBACK to empty string because
# when FAKEUSERAGENT_FALLBACK is not provided in the settings,
# it returns AssertionError: fallback must be a string
FAKEUSERAGENT_FALLBACK = ""
# Hardcoded UserAgent string, that is used if  FakeUserAgentProvider fail.
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:131.0) Gecko/20100101 Firefox/131.0"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Set settings whose default value is deprecated to a future-proof value
FEED_EXPORT_ENCODING = "utf-8"

FEED_EXPORTERS = {
    "xlsx": "scrapy_xlsx.XlsxItemExporter",
}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
EXTENSIONS = {
    "src.extensions.exporters.DefaultScrapedItemsExporter": 0,
    "scrapy.extensions.feedexport.FeedExporter": None,
}

# set HTTPCACHE_ENABLED to True for development only
# may cause auth errors if used auth token expired!
# scrapy cache is located in `.scrapy` folder, so simply remove it
# in order to clean cache
HTTPCACHE_ENABLED = True
HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

TELNETCONSOLE_ENABLED = False
