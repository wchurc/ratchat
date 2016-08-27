import unittest

from selenium import webdriver

class TestChat(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Firefox()

    def tearDown(self):
        self.driver.close()

    def test_basic_chat_functionality(self):

        # Reggie loads page and sees a chat window
        self.driver.get('localhost:5000')
        assert 'ratchat' in self.driver.title

        # Reggie sends a message and sees that a username has been
        # assigned automatically
        chat_input = self.driver.find_element_by_id('chat_input')
        chat_input.clear()
        chat_input.send_keys('Hello room\n')
        elems = self.driver.find_elements_by_xpath(
            "//*[contains(text(), 'Hello room')]")
        assert len(elems) > 0

        # Reggie sees that the automatically assigned username shows
        # up in a window with all the other active users
        active_users_element = self.driver.find_element_by_id('chat_users')
        active_users = active_users_element.text.split('\n')
        for elem in elems:
            name = elem.text.split(':')[0]
            assert name in active_users

    def test_chat_commands(self):
        pass
        # Reggie saw a message from the server that showed him how
        # to see a list of commands he could use

        # Reggie decides to create a new unique username

    def test_rooms(self):
        pass
        # Reggie creates a new chat room

        # Reggie sees that he is the only person in the room

        # Reggie invites a friend to join him in the room

        # 
