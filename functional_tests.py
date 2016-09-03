import unittest

from selenium import webdriver

class TestChat(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Firefox()

    def tearDown(self):
        self.driver.close()

    def get_active_users(self):
        active_users_element = self.driver.find_element_by_id('chat_users')
        return active_users_element.text.split('\n')
    
    def get_message_list(self, filter_by=None):
        chat_window = self.driver.find_element_by_id('chat_window')
        messages = chat_window.text.split('\n')
        if filter_by is not None:
            return [message for message in messages if filter_by in message]
        return messages

    def send_input(self, string):
        chat_input = self.driver.find_element_by_id('chat_input')
        chat_input.clear()
        chat_input.send_keys(string + '\n')

    def test_basic_chat_functionality(self):

        # Reggie loads page and sees a chat window
        self.driver.get('localhost:5000')
        assert 'ratchat' in self.driver.title

        # Reggie sends a message and sees that a username has been
        # assigned automatically
        original_messages = self.get_message_list()
        self.send_input('Hello room')
        new_messages = self.get_message_list()
        assert len(new_messages) > len(original_messages)

        # Reggie sees that the automatically assigned username shows
        # up in a window with all the other active users
        active_users = self.get_active_users()
        
        name = self.get_message_list(filter_by='Hello room')[-1].split(':')[0]
        assert name in active_users

    def test_chat_commands(self):
        self.driver.get('localhost:5000')
        
        # Reggie saw a message from the server that showed him how
        # to see a list of commands he could use

        # Reggie decides to change his alias 

        self.send_input('/callme Reginald')
        self.send_input("What's my name?")
        messages = self.get_message_list(filter_by="What's my name?")
        name = messages[-1].split(':')[0]
        self.assertEqual(name, 'Reginald')

        # Reggie 

        # Reggie creates a new chat room

        # Reggie sees that he is the only person in the room

        # Reggie invites a friend to join him in the room

        # 
