import sys
import re
import time
import logging

import tweepy
from tweepy import OAuthHandler

import config


class TwitterAccount():
    def __init__(self, user="wylsacom"):
        self.user = user
        try:
            self.consumer_key = config.consumer_key
            self.consumer_secret = config.consumer_secret
            self.access_token = config.access_token
            self.access_secret = config.access_secret

            self.auth = OAuthHandler(self.consumer_key, self.consumer_secret)
            self.auth.set_access_token(self.access_token, self.access_secret)
            self.api = tweepy.API(self.auth, wait_on_rate_limit_notify=False)
        except tweepy.TweepError as exception:
            logging.exception(exception)
        self.get_tweets()

    def get_tweets(self):
        spec_user_tweets = tweepy.Cursor(self.api.user_timeline,
                                         id=self.user).items(1000)

        for tweet in spec_user_tweets:
            tweet.text = re.sub("\n", " ", tweet.text)
            self.write_to_file(f'"{tweet.text}";\n')
            try:
                replies = tweepy.Cursor(self.api.search,
                                        q=f"{self.user}",
                                        since_id=tweet.id).items()
                # repliesss = [self.write_to_file(reply.text)
                #              for reply in replies
                #              if reply.in_reply_to_status_id == tweet.id]

                for reply in replies:
                    if reply.in_reply_to_status_id == tweet.id:
                        self.write_to_file(f'"{reply.text}";\n')
                        break
                self.write_to_file("-----------------------\n")
            except tweepy.TweepError as error:
                logging.exception(error)
                time.sleep(1000)
                continue

    def write_to_file(self, text):
        with open(f'data/{self.user}.csv', 'w') as file:
            file.write(text)


if __name__ == '__main__':
    TwitterAccount(user="realDonaldTrump")
