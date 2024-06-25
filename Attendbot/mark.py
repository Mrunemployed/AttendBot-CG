from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException,NoSuchElementException
from bs4 import BeautifulSoup
import time
import datetime
import pandas as pd
from . import DataIn
# import DataIn
import logging
import sys
import os
import re


path = os.path.abspath(os.path.dirname(__file__))
logs_dir = os.path.join(path,"logs")
if not os.path.exists(logs_dir):
    os.mkdir(logs_dir)
print("Find logs at:",logs_dir)
path_reports = os.path.abspath(os.path.dirname(__file__))
reports_dir = os.path.join(path_reports,"reports")
if not os.path.exists(reports_dir):
    os.mkdir(reports_dir)
print("Find attendance reports at:",reports_dir)

logging.basicConfig(filename=f'{logs_dir}\\{datetime.datetime.strftime(datetime.datetime.today(),"%Y-%m-%d")}.log',format='%(asctime)s %(message)s',filemode='a')
log = logging.getLogger()
log.setLevel(logging.INFO)


class attendence(DataIn.Bribe):

    def __init__(self,**kwargs) -> None:
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--start-maximized")
        if len(kwargs.keys()) > 0:
            if "mode" in kwargs.keys() and "month" in kwargs.keys():
                self.month = kwargs["month"]
            elif "month" in kwargs.keys():
                self.month = kwargs["month"]
            else:
                log.info("User has chosen to proceed with headless mode")
                print("Proceeding with headless mode...")
                self.options.add_argument("--headless=old")
                self.month = datetime.datetime.now().month-1
        else:
            log.info("User has chosen to proceed with headless mode")
            print("Proceeding with headless mode...")
            self.month = datetime.datetime.now().month-1
            self.options.add_argument("--headless=old")
            
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.get("https://talent.capgemini.com/in")
        log.info("getting URL:https://talent.capgemini.com/in ")
        self.df = pd.DataFrame()
        
    def wait_if_exists(self,reference,mode):
        retries = 0
        exp = 0
        while retries < 10 and exp <=1:
            try:
                time.sleep(1)
                if mode == 'CSS_SELECTOR':
                    self.driver.find_element(By.CSS_SELECTOR,reference)
                elif mode == 'XPATH':
                    self.driver.find_element(By.XPATH,reference)
                else:
                    pass
            except NoSuchElementException as ne:
                print(f"Waiting for PingID Authentication")
                exp+=1
                retries+=1
                continue
        if exp > 0 :
            return False
        else:
            return True
        
    def check_if_exists(self,reference,mode):
        retries = 0
        element = None
        while retries < 10:
            try:
                time.sleep(1)
                if mode == 'CSS_SELECTOR':
                    element = self.driver.find_element(By.CSS_SELECTOR,reference)
                    return element
                elif mode == 'XPATH':
                    element = self.driver.find_element(By.XPATH,reference)
                    return element
                else:
                    pass
                retries+=1
            except NoSuchElementException as err:
                retries+=1
                print(f"checking for pop-up retrying....{retries}")
                continue
            return element
            

    def goto_shiftallowance_page(self):
        
        try:
            log.info("Waiting for PingID Authentication..")
            print("checking for PingID approval....")
            check_auth = self.wait_if_exists(mode="CSS_SELECTOR",reference="a#usecodebutton")
            print("PingID approval received continuing....")
            print(check_auth)
            if check_auth:
                return False
            else:
                pass

            check = self.check_if_exists(reference="div#splashscreen-container",mode='CSS_SELECTOR')
            if check is None:
                log.info("pop-up not found No Action required")
                print("pop-up not found No Action taken...")
            else:
                WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.XPATH,"//span/button[@class='close_popin_btn']")))
                self.driver.find_element(By.XPATH,"//span/button[@class='close_popin_btn']").click()
                log.info("pop-up not found and handled")
                print("Pop-up handled....")
            print("Continiuing process....")
            WebDriverWait(self.driver,30).until(EC.presence_of_element_located((By.CSS_SELECTOR,".tool")))
            self.driver.find_element(By.XPATH,"//ul/li/a[@title='India Application Portal']").click()
            # time.sleep(5)
            self.driver.switch_to.window(self.driver.window_handles[-1])
            WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.XPATH,"//ul/li[@aria-haspopup='Menu_CAP:submenu:34']")))
            ac = ActionChains(self.driver)
            menu = self.driver.find_element(By.XPATH,"//ul/li[@aria-haspopup='Menu_CAP:submenu:34']")
            ac.move_to_element(menu).perform()
            shift_option = self.driver.find_element(By.XPATH,"//ul/li/a[starts-with(@href,'https://shift')]")
            ac.move_to_element(shift_option).click().perform()
            # time.sleep(5)
            self.driver.switch_to.window(self.driver.window_handles[-1])
            WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.CSS_SELECTOR,"li#liattendance")))
            self.driver.find_element(By.CSS_SELECTOR,"li#liattendance").click()
            self.driver.find_element(By.XPATH,"//ul/li[@id='liattendance']/ul[@class='dropdown-menu']/li/a").click()
            WebDriverWait(self.driver,30).until(EC.visibility_of_element_located((By.XPATH,"//a[@id='self-attendance']")))
            self.driver.find_element(By.XPATH,"//a[@id='self-attendance']").click()
            log.info(f"Scraper has successfully performed the task attendence.goto_shiftallowance_page")
            print("Scraper has successfully performed the task attendence.goto_shiftallowance_page")
            return True
        except TimeoutException as te:
            log.setLevel(logging.ERROR)
            log.error(f"Authentication request Timed out please try again error: {te}")
            print("Authentication request timed out, please re-run the program")
            return False
        except Exception as e:
            log.setLevel(logging.ERROR)
            log.error(f"Encountered error at attendence.goto_shiftallowance_page -> {e}")
            print(e)
            return False
    
    def scrape_attendence(self):
        try:
            WebDriverWait(self.driver,30).until(EC.visibility_of_element_located((By.XPATH,"//select[@id='e1']")))
            self.driver.find_element(By.XPATH,f"//select[@id='e1']/option[@value={self.month}]").click()
            WebDriverWait(self.driver,30).until(EC.visibility_of_element_located((By.XPATH,"//table/tbody/tr/td/div[@class='EmployeeID']")))
            soup = BeautifulSoup(self.driver.page_source,"html.parser")
            table = soup.find("table",{"id":"Table_report"})
            df_table = pd.read_html(str(table))
            df = df_table[0]
            self.df = df
            df.to_csv(f"{reports_dir}\\{self.month}-source-attendence-data.xlsx",index=False)
            log.info(f"Scraper has successfully performed the task attendence.scrape_attendence")
            print("Scraper has successfully performed the task attendence.scrape_attendence")
            return True
        except Exception as e:
            log.setLevel(logging.ERROR)
            log.error(f"Encountered error at attendence.scrape_attendence -> {e}")
            return False

    def identify_changes(self):
        make_df = self.manipulate(self.df)
        print(make_df)
        if isinstance(make_df,pd.DataFrame):
            shrink_df = make_df[make_df.Mode != "NoValue"]
            shrink_df = shrink_df[shrink_df.Mode != "ignore"]
            log.info(shrink_df)
            if shrink_df.empty:
                log.info(f"Looks like you're up to date for {self.month} month on Shift claims \n {make_df}")
                print(f"Looks like you're up to date for {self.month} month on Shift claims")
            else:
                    
                for i,j in shrink_df.iterrows():
                    if "Manual Swipe Attendence" in shrink_df.loc[i,"Mode"]:
                        make_df.loc[i,"Status"] = "Manual Swipe Attendence In-Progress"
                        status = self.apply_attendence(series=j,idx=i,work_mode="wfh")
                        make_df.loc[i,"Status"] = status
                        
                    elif "Swipe Adjustment" in shrink_df.loc[i,"Mode"]:
                        make_df.loc[i,"Status"] = "Swipe Adjustment In-Progress"
                        status = self.apply_attendence(series=j,idx=i,work_mode="swipe_adjustment")
                        make_df.loc[i,"Status"] = status
                        
                    else:
                        log.error(f"Encountered error at DataIn.Bribe.identify_changes  -> \\n {make_df}")
            make_df.to_csv(f"{reports_dir}\\{datetime.datetime.now().month-1}-attendance-completion.csv",index=False)
        else:
            log.setLevel(logging.ERROR)
            log.error(f"Encountered error at DataIn.Bribe.manipulate -> {make_df}")

    
    #Applies attendence as swipe adjustment or Manual attendance
    def apply_attendence(self,series:pd.Series,idx,work_mode:str):
        try:
            print(f"Trying to apply attendence for {series['Date']}...")
            print("Check logs for more info!")
            # log.setLevel(logging.DEBUG)
            log.info(f"Applying attendence as {work_mode}")
            log.info(series)
            series = series.to_frame().T
            
            WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.CSS_SELECTOR,"a#Self-team")))
            self_tab = self.driver.find_element(By.CSS_SELECTOR,"a#Self-team")
            # CHECK IF THE "SELF" TAB IS CURRENTLY OPEN
            log.info("CHECK IF THE SELF TAB IS CURRENTLY OPEN")
            if "active" not in self_tab.get_attribute("class"):
                self.driver.find_element(By.CSS_SELECTOR,"a#Self-team").click()
                log.info("SELF TAB NOT ACTIVE, SWTICHING TO IT")
            else:
                log.info("SELF TAB CURRENTLY ACTIVE, NO ACTION TAKEN")
            #GO TO ADD MANUAL/ SWIPE ATTENDENCE PAGE
            log.info("GO TO ADD MANUAL/ SWIPE ATTENDENCE PAGE")
            WebDriverWait(self.driver,30).until(EC.presence_of_element_located,((By.XPATH,"//*[@class='custom-button manual-team-add-button']")))
            self.driver.find_element(By.XPATH,"//*[@class='custom-button manual-team-add-button']").click()

            # CHECK IF THE WORK MODE IS WFH OR SWIPE ADJUSTMENT
            log.info("CHECK IF THE WORK MODE IS WFH OR SWIPE ADJUSTMENT")
            if "wfh" in work_mode:
                # SELECT DROPDOWN OPTION AS MANUAL ATTENDENCE
                log.info(f"SELECT DROPDOWN OPTION AS MANUAL ATTENDENCE TYPE:{work_mode}")
                time.sleep(3)
                WebDriverWait(self.driver,10).until(EC.element_to_be_clickable((By.XPATH,"//select[@name='RequestTypeId']/option[@value='Manual Attendance']")))
                self.driver.find_element(By.XPATH,"//select/*[@value='Manual Attendance' and position()=1]").click()
                # SELECT REGULARIZATION TYPE AND HANDLE POP UP ALERT
                log.info("SELECT REGULARIZATION TYPE AND HANDLE POP UP ALERT")
                WebDriverWait(self.driver,10).until(EC.element_to_be_clickable((By.XPATH,"//select[@name='RegularizationType']/option[@value='Working From Home']")))
                self.driver.find_element(By.XPATH,"//select[@name='RegularizationType']/option[@value='Working From Home']").click()
                WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.CSS_SELECTOR,"div#Common-Error-Alert-Model[aria-hidden='false']")))
                WebDriverWait(self.driver,10).until(EC.element_to_be_clickable((By.XPATH,"//div[@id='Common-Error-Alert-Model' and @aria-hidden='false']/descendant::node()/button")))
                self.driver.find_element(By.XPATH,"//div[@id='Common-Error-Alert-Model' and @aria-hidden='false']/descendant::node()/button").click()
            elif "swipe_adjustment" in work_mode:
                # SELECT DROPDOWN OPTION AS SWIPE ADJUSTMENT
                log.info(f"SELECT DROPDOWN OPTION AS SWIPE ADJUSTMENT TYPE:{work_mode}")
                WebDriverWait(self.driver,10).until(EC.visibility_of_element_located((By.XPATH,"//select[@name='RequestTypeId']/option[@value='Swipe Ad']")))
                self.driver.find_element(By.XPATH,"//select[@name='RequestTypeId']/option[@value='Swipe Ad']").click()
            else:
                pass
            # ENTER DATE START
            log.info("TRYING TO INSERT DATE")
            WebDriverWait(self.driver,30).until(EC.element_to_be_clickable((By.XPATH,"//input[@name='ReqAttendanceDate']")))
            date_field = self.driver.find_element(By.XPATH,"//input[@name='ReqAttendanceDate']")
            date = datetime.datetime.strptime(series.loc[idx,"Date"],"%d-%b-%Y")
            format_date = datetime.datetime.strftime(date,"%d-%m-%Y")
            log.info(f"Date to be inserted:{format_date}")
            self.driver.execute_script(f"arguments[0].setAttribute('value', '{format_date}')", date_field)
            # ENTER DATE END
            log.info("DATE ENTERED SUCCESSFULLY")

            # SEND TIMEFRAME
            log.info("SEND TIMEFRAME")
            WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.CSS_SELECTOR,"input#InTime")))
            # in_time_field = self.driver.find_element(By.CSS_SELECTOR,"input#InTime")
            # out_time_field = self.driver.find_element(By.CSS_SELECTOR,"input#OutTime")
            # self.driver.execute_script("arguments[0].setAttribute('value', '14:00')", in_time_field)
            # self.driver.execute_script("arguments[0].setAttribute('value', '23:30')", out_time_field)
            self.driver.find_element(By.CSS_SELECTOR,"input#InTime").clear()
            self.driver.find_element(By.CSS_SELECTOR,"input#InTime").send_keys("14:00")
            self.driver.find_element(By.CSS_SELECTOR,"input#OutTime").clear()
            self.driver.find_element(By.CSS_SELECTOR,"input#OutTime").send_keys("23:30")
            self.driver.find_element(By.CSS_SELECTOR,"a#submitRecord").click()
            # HANDLE POP UP ALERT UPON SUBMIT
            log.info("HANDLE POP UP ALERT UPON SUBMIT")
            WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.CSS_SELECTOR,"div#submit-attendance[aria-hidden='false']")))
            WebDriverWait(self.driver,10).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"button#SaveRecords")))
            self.driver.find_element(By.CSS_SELECTOR,"button#SaveRecords").click()
            # HANDLE POP UP ALERT UPON CONFIRMATION OF SUBMIT
            log.info("HANDLE POP UP ALERT UPON CONFIRMATION OF SUBMIT")
            WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.CSS_SELECTOR,"div#submit-successfully-attendance[aria-hidden='false']")))
            WebDriverWait(self.driver,10).until(EC.element_to_be_clickable((By.XPATH,"//div[@id='submit-successfully-attendance' and @aria-hidden='false']/descendant::node()/button")))
            self.driver.find_element(By.XPATH,"//div[@id='submit-successfully-attendance' and @aria-hidden='false']/descendant::node()/button").click()
            print(f"Successfully applied attendence for date: {series['Date']}")
            return f'Successful for Date: {series.loc[idx,"Date"]}'
            # return "failed"
        except Exception as e:
            log.setLevel(logging.ERROR)
            log.error(f"Encountered error at attendence.apply_attendance -> {e} \n data: {series} \n type: {work_mode}")
            print(f"Failed to apply attendence for date: {series['Date']}")
            if "https://shiftallowance.in.capgemini.com/AMSAttendanceRequest/SelfAttendance" in self.driver.current_url:                
                WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.CSS_SELECTOR,"li#liattendance")))
                self.driver.find_element(By.CSS_SELECTOR,"li#liattendance").click()
                self.driver.find_element(By.XPATH,"//ul/li[@id='liattendance']/ul[@class='dropdown-menu']/li/a").click()
            return "Failed"
        
    
def main():
    if len(sys.argv) > 1:
        if '-i' in sys.argv:
            if '-m' in sys.argv:
                indx = sys.argv.index('-m')
                if len(sys.argv) >= indx+1 and re.search("[0-9]",str(sys.argv)) != None:
                    att = attendence(mode="show",month=int(sys.argv[indx+1]))
                else:
                    log.error("Month value not entered")
                    print("Month Data not found - \n enter flag like: py -m Attendbot.mark -m 8 -<ADDITional Flag>")
                    att = attendence(mode="show")
            else:
                att = attendence(mode="show")
        else:
            if '-m' in sys.argv:
                indx = sys.argv.index('-m')
                if len(sys.argv) >= indx+1 and re.search("[0-9]",str(sys.argv)) != None:
                    att = attendence(month=int(sys.argv[indx+1]))
                else:
                    log.error("Month value not entered")
                    print("Month Data not found - \n enter flag like: py -m Attendbot.mark -m 8 -<ADDITional Flag>")
                    att = attendence()
            else:
                log.info("No Flags entered")
                att = attendence()
    else:
        att = attendence()

    is_success = att.goto_shiftallowance_page()
    if is_success:
        is_success = att.scrape_attendence()
        if is_success :
            att.identify_changes()
        else:
            log.setLevel(logging.INFO)
            log.error("Closing the program because of error")
    else:
        log.setLevel(logging.INFO)
        log.error("Closing the program because of error")

if __name__=='__main__':
    main()