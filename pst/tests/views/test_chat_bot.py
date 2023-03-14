from django.test import Client, TestCase

class ChatBotTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_chat_bot_response(self):
        response = self.client.post('/chat_bot/', {'user_input': 'hi'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Hello! How may I help you?', response.content)
    
    def test_chat_bot_psc_response(self):
        response = self.client.post('/chat_bot/', {'user_input': 'personal spending tracker'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Our Personal Spending Tracker helps you keep track of your daily expenses and budget.', response.content)
    
    def test_chat_bot_budget_response(self):
        response = self.client.post('/chat_bot/', {'user_input': 'budget'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You can use our Personal Spending Tracker to set budgets for different categories of expenses.', response.content)
    
    def test_chat_bot_expense_response(self):
        response = self.client.post('/chat_bot/', {'user_input': 'expense'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You can log all your expenses on our Personal Spending Tracker, including the date, category, and amount spent.', response.content)
    
    def test_chat_bot_track_response(self):
        response = self.client.post('/chat_bot/', {'user_input': 'track'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Our Personal Spending Tracker is designed to help you keep track of your daily expenses, budget, and savings.', response.content)

    def test_chat_bot_forum_response(self):
        response = self.client.post('/chat_bot/', {'user_input': 'forum'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Our online forum is a great place to connect with other users, share tips and advice, and discuss personal finance topics. You can join the forum by simply clicking on the Forum button on the home page.", response.content)

    def test_chat_bot_help_response(self):
        response = self.client.post('/chat_bot/', {'user_input': 'help'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'you can try asking about pst, budget, expense, track, forum, report, rewards, category, calender for more information.', response.content)

    def test_chat_bot_report_response(self):
        response = self.client.post('/chat_bot/', {'user_input': 'report'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Our report feature can create a chart of your expenses and provide a detailed list of your spending.', response.content)

    def test_chat_bot_reward_response(self):
        response = self.client.post('/chat_bot/', {'user_input': 'reward'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'By using our Personal Spending Tracker consistently, you can earn points which can be redeemed for various rewards in our reward shop.', response.content)

    def test_chat_bot_category_response(self):
        response = self.client.post('/chat_bot/', {'user_input': 'category'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'While we offer default categories for both income and expenses, you always have the option to customize them to fit your personal preferences and needs in the settings!', response.content)

    def test_chat_bot_calender_response(self):
        response = self.client.post('/chat_bot/', {'user_input': 'calender'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Our calendar feature can assist you in monitoring your income and expenses for the current month, allowing you to quickly determine your spending and effectively manage your financial plan with greater efficiency!', response.content)


    def test_chat_bot_response_when_input_is_close(self):
        response = self.client.post('/chat_bot/', {'user_input': 'dates'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Our calendar feature can assist you in monitoring your income and expenses for the current month, allowing you to quickly determine your spending and effectively manage your financial plan with greater efficiency!', response.content)