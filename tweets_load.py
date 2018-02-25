import sys
import re
import argparse
import time
import logging

import tweepy
from tweepy import OAuthHandler

import config


class StreamListener(tweepy.StreamListener):
    def on_status(self, status):
        tw = TwitterAccount()
        tw.write_to_file(f"{status.text}\n")

    def on_error(self, status_code):
        if status_code == 420:
            return False


class TwitterAccount():
    def __init__(self, user="wylsacom"):
        self.user = user
        self.num_of_tweets = 10
        self.num_of_repl = 20
        self.limit = 0
        self.get_api()
        self.get_tweets()

    def get_api(self):
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
        return self.api

    def get_tweets(self):
        user_tweets = self.api.user_timeline(id=self.user,
                                             count=self.num_of_tweets,
                                             pages=10)
        self.limit += len(user_tweets)

        for num, tweet in enumerate(user_tweets):
            tweet.text = re.sub("\n", " ", tweet.text)
            print(num, tweet.text)
            self.write_to_file(f"Tweet number {num}: \n")
            if self.limit >= 320:
                print("No more tweets")
                print("Sleep for 15min....")
                self.limit = 0
                time.sleep(900)
                continue
            else:
                try:
                    # replies = self.api.search(q=f"@{self.user}",
                    #                           since_id=tweet.id)
                    status = tweepy.Cursor(self.api.search,
                                           q=f"@{self.user}",
                                           since_id=tweet.id,
                                           rpp=self.num_of_repl,
                                           pages=1
                                           ).items()
                    self.limit += self.num_of_repl
                    for reply in status:
                        if reply.in_reply_to_status_id == tweet.id:
                            reply_user = str(reply.user.screen_name).strip()
                            self.write_to_file(f'"{self.user} tweeted: {tweet.text}";\n')
                            self.write_to_file(f'"{reply_user} replied: {reply.text}";\n')
                            self.write_to_file("-----------------------\n")
                            break
                            print("----------Нашел ответ!----------\n")
                            print("Ищу ответ на следующий твит\n")

                except tweepy.TweepError as error:
                    logging.exception(error)
                    time.sleep(900)
                    continue

    def write_to_file(self, text):
        with open(f'data/{self.user}.csv', 'a') as file:
            file.write(text)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", help="Choose the user whose tweets to download")
    args = parser.parse_args()
    if args.username:
        print(f"Searching {args.username} tweets")
        TwitterAccount(user=args.username)
    else:
        TwitterAccount()

    # streamListener = StreamListener()
    # stream = tweepy.Stream(auth=api.auth, listener=streamListener)
    # stream.filter(follow=["284168384"])
