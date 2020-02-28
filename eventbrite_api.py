import sys, os
sys.path.append(os.path.expanduser('~/projects/bots'))
from bots import Bot
from eventbrite import Eventbrite
from time import sleep

class EventBot(Bot):
    def __init__(self, token, credentials={'email': 'user@domain.com', 'password': 'pword'}):
        super().__init__()
        if token:
            self.eventbrite = Eventbrite(token)
        self.credentials = credentials
        self.sign_in()

    def get_live_events(self):
        r = self.eventbrite.get('/users/me/owned_events')
        r = [e for e in r['events'] if e['status'] == 'live']
        return r

    def sign_in(self):
        self.driver.get('https://www.eventbrite.co.uk/signin')
        sleep(1)
        if 'signin' not in self.driver.current_url:
            return
        email = self.driver.find_element_by_xpath('//input[@type="email"]')
        email.send_keys(self.credentials['email'])
        self.click_btn('get started')
        sleep(1)
        password = self.driver.find_element_by_xpath('//input[@type="password"]')
        password.send_keys(self.credentials['password'])
        self.click_btn('log in')        

    def toggle_custom_questions(self):
        checkbox = self.driver.find_element_by_xpath('//input[@id="switchCustomizeQuestions"]')
        if checkbox.is_selected():
            return
        switch = self.driver.find_element_by_xpath('//div[@id="customizeCheckoutQuestions"]')
        switch = switch.find_element_by_xpath('div/div/a')
        switch.click()

    def add_questions(self, event_id, questions):
        self.driver.get(f'https://www.eventbrite.co.uk/questions?eid={event_id}')
        # sleep(1)
        self.toggle_custom_questions()
        for q in questions:
            custom_qs = self.driver.find_elements_by_xpath('//div[@id="customQuestionsDiv"]/div')
            custom_qs_text = [q.text for q in custom_qs]
            for r in ['\nDelete', '\nMove down', '\nMove up', '\nSettings']:
                custom_qs_text = [q.replace(r, '') for q in custom_qs_text]
            # custom_qs_text = [q for q  in custom_qs_text if q != '']
            # print(custom_qs_text)
            if q['question'] in custom_qs_text:
                print('ALREADY EXISTS:', q['question'])
            else:
                print('adding question:', q['question'])
                add_question = custom_qs[-1 ].find_element_by_xpath('a')
                add_question.click()
                sleep(1)
                question_prompt = self.driver.find_element_by_xpath('//input[@id="id_group-parent-question"]')
                question_prompt.send_keys(q['question'])
                question_type_input = self.driver.find_element_by_xpath('//select[@id="id_group-parent-question_type"]')
                question_type_input.send_keys(q['type'])
                sleep(1)
                if q['type'] == 'Checkboxes':
                    for idx, option in enumerate(q['options']):
                        try:
                            option_input = self.driver.find_element_by_xpath(f'//input[@id="id_group-qchoices-{idx}-answer"]')
                        except Exception as e:
                            print('ERROR:', e)
                            self.click_btn('add another option')
                            # self.driver.find_element_by_xpath('//')
                            option_input = self.driver.find_element_by_xpath(f'//input[@id="id_group-qchoices-{idx}-answer"]')
                        option_input.send_keys(option)

                    # SET CONDITIONAL LOGIC FOR THIS QUESTION
                    if 'conditionals' in q.keys():
                        print('SETTING CONDITIONAL LOGIC')
                        # CLICK BTN TO ENABLE CONDITIONAL LOGIC IF NOT ALREADY ENABLED
                        enable_conditional_logic_btn = self.driver.find_element_by_xpath('//input[@id="enable_conditional_logic"]')
                        if not enable_conditional_logic_btn.is_selected():
                            self.click_btn('Add conditional sub-questions')
                        # ADD CONDITIONAL LOGIC
                        for cidx, key in enumerate(q['conditionals']):  
                            self.click_btn('add another sub-question')
                            option_selected = self.driver.find_element_by_xpath(f'//select[@id="id_group-qlogic-{cidx}-qchoice"]')
                            option_selected.send_keys(key)
                            ask_input = self.driver.find_element_by_xpath(f'//input[@id="id_group-questions-{cidx+1}-question"]')
                            ask_input.send_keys(q['conditionals'][key]['question'])
                self.driver.find_element_by_xpath('//input[@id="question_save"]').click()
                # self.click_btn('save')
        print('toggling REQUIRED flag')
        custom_qs = self.driver.find_elements_by_xpath('//div[@id="customQuestionsDiv"]/div')
        custom_qs_text = [q.text for q in custom_qs]
        for r in ['\nDelete', '\nMove down', '\nMove up', '\nSettings']:
            custom_qs_text = [q.replace(r, '') for q in custom_qs_text]
        for q in questions: # assert that 'required' is correctly set to true or false
            if 'required' not in q.keys(): break # if required not specified, leave as default (CHANGE LATER TO HAVE REQUIRED=FALSE BY DEFAULT?)
            assert isinstance(q['required'], bool)
            custom_q = custom_qs[custom_qs_text.index(q['question'])]
            switch = custom_q.find_elements_by_xpath('div/div/a')[-1]
            checkbox = custom_q.find_elements_by_xpath('div/div/input')[-1]
            if checkbox.is_selected() and q['required'] == False: # if already marked as required but we don't want it required
                switch.click() # toggle the switch

