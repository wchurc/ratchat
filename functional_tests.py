import time
import unittest
import os

import redis
from selenium import webdriver

os.environ['RATCHAT_TESTING'] = 'False'
from ratchat import redis_db
assert type(redis_db) == redis.client.StrictRedis
redis_db.flushall()

host = "http://0.0.0.0:5000"

class TestChat(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome()

    def tearDown(self):
        self.driver.close()

    def get_active_users(self):
        active_users_element = self.driver.find_element_by_id('users-window')
        return active_users_element.text.split('\n')

    def get_message_list(self, filter_by=None, driver=None):
        if driver is None:
            driver = self.driver
        chat_window = driver.find_element_by_id('chat-window')
        messages = chat_window.text.splitlines()
        if filter_by is not None:
            return [message for message in messages if filter_by in message]
        return messages

    def send_input(self, string, driver=None):
        if driver is None:
            driver = self.driver
        chat_input = driver.find_element_by_id('chat-input')
        chat_input.clear()
        chat_input.send_keys(string)
        chat_input.submit()

    def test_basic_chat_functionality(self):

        # Reggie loads page and sees a chat window

        self.driver.get(host)
        self.assertIn('ratchat', self.driver.title)

        # Reggie sends a message and sees that a username has been
        # assigned automatically

        original_messages = self.get_message_list()
        self.send_input('Hello room')
        new_messages = self.get_message_list()
        self.assertGreater(len(new_messages), len(original_messages))

        # Reggie sees that the automatically assigned username shows
        # up in a window with all the other active users

        time.sleep(1)
        name = self.get_message_list(filter_by='Hello room')[-1].split(':')[0]
        active_users = self.get_active_users()

        self.assertIn(name, active_users)

    def test_chat_commands(self):
        self.driver.get(host)

        # Reggie saw a message from the server that showed him how
        # to see a list of commands he could use

        messages = self.get_message_list(filter_by='server')
        self.assertIn('server: Type /help for a list of commands.', messages)

        # Reggie decides to change his alias

        self.send_input('/callme Reginald')
        self.send_input("What's my name?")
        messages = self.get_message_list(filter_by="What's my name?")
        name = messages[-1].split(':')[0]
        self.assertEqual(name, 'Reginald')

        # Reggie decides to create a password protected login

        self.send_input('/login testuser1 testpass')
        messages = self.get_message_list(filter_by='server')
        self.assertIn('server: Login Successful', messages)
        time.sleep(2)
        active_users = self.get_active_users()
        self.assertIn('testuser1', active_users)

        # A friend logs in as testuser2 and a stranger enters the chat

        driver2 = webdriver.Firefox()
        driver2.get(host)
        time.sleep(2)
        self.send_input('/login testuser2 testpass', driver=driver2)
        time.sleep(2)

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--incognito')
        driver3 = webdriver.Chrome(chrome_options=chrome_options)
        driver3.get(host)

        time.sleep(2)

        # Reggie notices the friend in the active users window

        active_users = self.get_active_users()
        self.assertIn('testuser2', active_users)

        # Reggie sends a private message to his friend and sees it in his
        # chat_window

        self.send_input('This is public')
        self.send_input('/msg testuser2 This is private.')
        time.sleep(2)
        last_message = self.get_message_list()[-1]
        self.assertIn('This is private.', last_message)

        # Reggie's friend also sees the message

        last_message = self.get_message_list(driver=driver2)[-1]
        self.assertIn('This is private.', last_message)

        # The stranger did not receive the message

        last_message = self.get_message_list(driver=driver3)[-1]
        self.assertIn('This is public', last_message)
        driver3.close()

        # testuser2 logs off and is no longer visible in the users window

        driver2.quit() # Using quit instead of close because of issue with Selenium
        time.sleep(2)
        active_users = self.get_active_users()
        self.assertNotIn('testuser2', active_users)

        # Reggie can't send any more private messages to testuser2.
        # The server notifies him that testuser2 is not available

        self.send_input('/msg testuser2 You still here?')
        last_message = self.get_message_list()[-1]
        self.assertIn('testuser2 is not currently active', last_message)


    def test_registered_names(self):
        pass
