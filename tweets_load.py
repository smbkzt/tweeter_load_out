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
        self.get_authorization()
        self.get_tweets()

    def get_authorization(self):
        try:
            self.consumer_key = config.consumer_key
            self.consumer_secret = config.consumer_secret
            self.access_token = config.access_token
            self.access_secret = config.access_secret

            self.auth = OAuthHandler(self.consumer_key, self.consumer_secret)
            self.auth.set_access_token(self.access_token, self.access_secret)
            self.api = tweepy.API(self.auth, wait_on_rate_limit_notify=True)
        except tweepy.TweepError as exception:
            logging.exception(exception)

    def get_tweets(self):
        user_tweets = self.api.user_timeline(id=self.user, count=200, pages=10)
        num_retrieved_tweets = 0
        num_retrieved_tweets += len(user_tweets)
        print(f"Счетчик твитов: {num_retrieved_tweets}")

        for tweet in user_tweets:
            tweet.text = re.sub("\n", " ", tweet.text)
            self.write_to_file(f'"{self.user} tweeted: {tweet.text}";\n')

            if num_retrieved_tweets >= 320:
                print("No more tweets")
                print("Sleep for 1000ms....")
                num_retrieved_tweets = 0
                time.sleep(10000)
                continue
            else:
                try:
                    replies = self.api.search(q=f"@{self.user}",
                                              since_id=tweet.id, pages=2)
                    num_retrieved_tweets += len(replies)

                    print(f"Найдено ответов в цикле: {len(replies)}")
                    print(f"Счетчик твитов: {num_retrieved_tweets}")

                    for reply in replies:
                        if reply.in_reply_to_status_id == tweet.id:
                            reply_user = str(reply.user.screen_name).strip()
                            self.write_to_file(f'"{reply_user} replied {reply.text}";\n')
                            print("----------Нашел ответ!----------")

                    self.write_to_file("-----------------------\n")
                except tweepy.TweepError as error:
                    logging.exception(error)
                    time.sleep(1000)
                    continue

    def write_to_file(self, text):
        with open(f'data/{self.user}.csv', 'a') as file:
            file.write(text)


if __name__ == '__main__':
    TwitterAccount(user="wylsacom")
