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
    
    def test_chat_bot_saving_response(self):
        response = self.client.post('/chat_bot/', {'user_input': 'saving'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Our Personal Spending Tracker can help you track your savings and keep you on track to reach your financial goals.', response.content)

    def test_chat_bot_finance_response(self):
        response = self.client.post('/chat_bot/', {'user_input': 'finance'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'With the PST, you can take control of your personal finances and make informed decisions about your spending and saving.', response.content)
       