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
import subprocess
import os
import re
import git
import json


path = os.path.abspath(os.path.dirname(__file__))
logs_dir = os.path.join(path,"logs")
if not os.path.exists(logs_dir):
    os.mkdir(logs_dir)
print("\033[32m Find logs at:",logs_dir,"\033[37m")

path_reports = os.path.abspath(os.path.dirname(__file__))
current_attendance = os.path.join(path_reports,"current_attendance")
if not os.path.exists(current_attendance):
    os.mkdir(current_attendance)
# print("Find attendance reports at:",current_attendance)

path_completed = os.path.abspath(os.path.dirname(__file__))
completed = os.path.join(path_reports,"completed")
if not os.path.exists(current_attendance):
    os.mkdir(current_attendance)
print("\033[36m Find attendance reports at:",completed,"\033[37m \n")


logging.basicConfig(filename=f'{logs_dir}\\{datetime.datetime.strftime(datetime.datetime.today(),"%Y-%m-%d")}.log',format='%(asctime)s %(message)s',filemode='a')
log = logging.getLogger()
log.setLevel(logging.INFO)

class updates():
    def __init__(self) -> None:
        path = None
        try:
            with open('config.json') as file:
                conf = json.loads(file)
                path = conf['git_repo']
                print(f"\033[44m Initializing repo at : {path} \033[40m")
                print("\033[36m Initialized Repo executing... \033[37m")
                self.ginit = git.Repo(path)
        except Exception as err:
            print(err)
            log.error(f"Could not find the config file, error: {err}")
            self.ginit = None
        finally:
            if not path:
                path = os.path.abspath(os.path.dirname(__file__))
                path = os.path.join(path,"..")
                self.ginit = git.Repo(path)
            
            
            

    def pull_this(self):
        updated = False
        if not self.ginit:
            return False
        else:
            pass
        current = self.ginit.head.commit
        self.ginit.remotes.origin.pull()
        log.info("Attempting pull from repo...")
        if current != self.ginit.head.commit:
            log.info("Pulled changes from repo.")
            print("\033[42m new updates found! \033[40m")
            updated = True
        else:
            log.info("No new updates detected. Proceeding...")
            print("no new updates found. Proceeding....")
        return updated
        
    def remove_older_builds(self,path):

        import shutil
        try:
            log.info("Attempting to remove older builds and dependencies...")
            print("removing older builds....")
            build = os.path.exists(os.path.join(path,'build'))
            log.info(f"checking if path exists {os.path.join(path,'build')}...")
            if build:
                log.info("Found older builds removing...")
                print("older build found, now removing....")
                shutil.rmtree(os.path.join(path,"build"))
                print("Removed older builds")
                log.info("removed older builds")
            else:
                log.info(f"Invalid path: {os.path.join(path,'build')}")
                print("No older builds found")

            dirs = os.listdir(path=path)
            log.info(f"Checking for dirs in current folder: {dirs}")
            egg_info_dir = [x for x in dirs if re.search(".egg-info$",x)][0]
            egg_info = os.path.exists(os.path.join(path,egg_info_dir))
            if egg_info:
                log.info("Found older builds removing...")
                print("older Metadata found, now removing....")
                shutil.rmtree(os.path.join(path,egg_info_dir))
                print("Removed older egg-info")
                log.info("removed older builds")
            else:
                log.info(f"Invalid path: {os.path.join(path,egg_info_dir)}")
                print("No older meta-data found.")

            return True

        except Exception as err:
            print("could not remove older builds \n Please report the problem to the Devs, in case the bot is not performing as expected.")
            log.error(f"Error while removing older builds: {err}")
            return False
    
    def update(self,name):
        try:
            log.info("At method: update. Attempting to update existing package")
            uninstall = subprocess.call([sys.executable, '-m', 'pip', 'uninstall', name])
            if uninstall == 1:
                log.info(f"Failed to uninstall {name}....")
                print(f"Failed to uninstall {name}, this may happen if your Python is not installed on PATH")
                print("Please uninstall the package and reinstall manually")
                return False
            else:
                log.info(f"uninstalled {name}....")
                path = os.path.abspath(os.path.dirname(__file__))
                path = os.path.join(path,"..")
                os.chdir(path=path)
                
                print("now trying to remove older builds...")
                remove_builds = self.remove_older_builds(path=path)

                install = subprocess.call([sys.executable, '-m', 'pip', 'install', '.'])
                if install == 1:
                    log.info(f"Failed to install {name}....")
                    print(f"Failed to install {name}, this may happen if your Python is not installed on PATH")
                    print("Please install the package and reinstall manually")
                    return False
                else:
                    return True

        except Exception as err:
            log.error(err)
            return False
        
    
class attendence(DataIn.Bribe):

    def __init__(self,**kwargs) -> None:
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--start-maximized")
        print(kwargs)
        if len(kwargs.keys()) > 0:
        
            if "mode" in kwargs.keys() and "month" in kwargs.keys():
                self.month = kwargs["month"]
                print("Interactive mode selected.. \nNow displaying...")
                log.info("Detected Interactive mode, Bot will now show the execution window.")
                log.info(f"Applying attendence for month: {self.month}")
                print(f"Bot will now apply attendence for month: {self.month}")

            elif "month" in kwargs.keys():
                self.month = kwargs["month"]
                log.info(f"Bot will now attendence for month: {self.month}")
                print(f"Bot will now apply attendence for month: {self.month}")
                log.info("User has chosen to proceed with headless mode")
                print("Proceeding with headless mode...")
                self.options.add_argument("--headless=old")

            elif "mode" in kwargs.keys():
                self.month = datetime.datetime.now().month-1
                print("Interactive mode selected.. \nNow displaying...")
                print(f"Month not specified by the user. Assuming previous month: {self.month} by default")
                log.info(f"Month not specified by the user. Assuming previous month: {self.month} by default")
            
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
                WebDriverWait(self.driver,30).until(EC.presence_of_element_located((By.XPATH,"//span/button[@class='close_popin_btn']")))
                self.driver.find_element(By.XPATH,"//span/button[@class='close_popin_btn']").click()
                log.info("pop-up not found and handled")
                print("Pop-up handled....")
            print("Continiuing process....")
            WebDriverWait(self.driver,30).until(EC.presence_of_element_located((By.CSS_SELECTOR,".tool")))
            self.driver.find_element(By.XPATH,"//ul/li/a[@title='India Application Portal']").click()
            # time.sleep(5)
            self.driver.switch_to.window(self.driver.window_handles[-1])
            WebDriverWait(self.driver,30).until(EC.presence_of_all_elements_located((By.XPATH,"//ul/li[@class='has-popup static']/a[contains(@class, 'static')]")))
            self.driver.find_element(By.TAG_NAME,"body").send_keys(Keys.CONTROL + 't')
            self.driver.get("https://shiftallowance.in.capgemini.com")

            # Menu removed for go->to Shift Allowance Page hardcoding URL for fix.
                # ac = ActionChains(self.driver)
                # menu = self.driver.find_elements(By.XPATH,"//ul/li[@class='has-popup static']/a[contains(@class, 'static')]")
                # menu_idx = menu.index([x for x in menu if re.search("finance",x.text,re.IGNORECASE)][0])
                # ac.move_to_element(menu[menu_idx]).perform()
                # shift_option = self.driver.find_element(By.XPATH,"//ul/li/a[starts-with(@href,'https://shift')]")
                # ac.move_to_element(shift_option).click().perform()
                # time.sleep(5)
                # self.driver.switch_to.window(self.driver.window_handles[-1])
    
            WebDriverWait(self.driver,30).until(EC.presence_of_element_located((By.CSS_SELECTOR,"li#liattendance")))
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
            # time.sleep(10)
            print("bot is reading the Attendence data...")
            animation = "|/-\\"
            idx = 0
            while idx<20:
                print(animation[idx % len(animation)], end="\r")
                idx += 1
                time.sleep(0.5)
            soup = BeautifulSoup(self.driver.page_source,"html.parser")
            table = soup.find("table",{"id":"Table_report"})
            df_table = pd.read_html(str(table),skiprows=1)
            # log.info(df_table)
            df = df_table[0]
            self.df = df
            log.info(df.columns)
            # log.info(df["Rostered shift"])
            df.to_csv(f"{current_attendance}\\{self.month}-source-attendence-data.csv",index=False)
            log.info(f"Scraper has successfully performed the task attendence.scrape_attendence")
            print("Scraper has successfully performed the task attendence.scrape_attendence")
            return True
        except Exception as e:
            log.setLevel(logging.ERROR)
            log.error(f"Encountered error at attendence.scrape_attendence -> {e}")
            return False

    def cleanup(self,path_to_df):
        if path_to_df:
            os.remove(path_to_df)
        else:
            print("Nothing to cleanup")

    def select_file(self):
        att_report = os.listdir(current_attendance)
        exp = re.compile(f"^[{self.month}]-[a-zA-Z]*")
        contents = [x for x in att_report if re.search(exp,x)][0]
        path = os.path.join(current_attendance,contents)
        return path
        
    def identify_changes(self):
        att_report = self.select_file()
        make_df = self.manipulate(att_report)
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

                    if "MSMA" in shrink_df.loc[i,"Mode"]:
                        make_df.loc[i,"Status"] = "Morning Shift Manual Swipe Attendence In-Progress"
                        print("Morning Shift Manual Swipe Attendence In-Progress...")
                        status = self.apply_attendence(series=j,idx=i,work_mode="wfh",tags="MS")
                        make_df.loc[i,"Status"] = status

                    elif "ASMA" in shrink_df.loc[i,"Mode"]:
                        make_df.loc[i,"Status"] = "Afternoon Shift Manual Swipe Attendence In-Progress"
                        print("Afternoon Shift Manual Swipe Attendence In-Progress...")
                        status = self.apply_attendence(series=j,idx=i,work_mode="wfh",tags="AS")
                        make_df.loc[i,"Status"] = status
                    
                    elif "MSSA" in shrink_df.loc[i,"Mode"]:
                        make_df.loc[i,"Status"] = "Morning Shift Swipe Adjustment In-Progress"
                        print("Morning Shift Swipe Adjustment In-Progress")
                        status = self.apply_attendence(series=j,idx=i,work_mode="swipe_adjustment",tags="MS")
                        make_df.loc[i,"Status"] = status

                    elif "AFSA" in shrink_df.loc[i,"Mode"]:
                        make_df.loc[i,"Status"] = "Afternoon Shift Swipe Adjustment In-Progress"
                        print("Afternoon Shift Swipe Adjustment In-Progress")
                        status = self.apply_attendence(series=j,idx=i,work_mode="swipe_adjustment",tags="AS")
                        make_df.loc[i,"Status"] = status
                        
                    else:
                        log.error(f"Encountered error at DataIn.Bribe.identify_changes  -> \\n {make_df}")
                        
            make_df.to_csv(f"{completed}\\{datetime.datetime.now().month-1}-attendance-completion.csv",index=False)
            self.cleanup(os.path.join(current_attendance,att_report[0]))
        else:
            log.setLevel(logging.ERROR)
            log.error(f"Encountered error at DataIn.Bribe.manipulate -> {make_df}")

    
    #Applies attendence as swipe adjustment or Manual attendance
    def apply_attendence(self,series:pd.Series,idx,work_mode:str,tags:str):
        try:
            print(f"Trying to apply attendence for {series['Date']}...")
            print("Check logs for more info!")
            # log.setLevel(logging.DEBUG)
            log.info(f"Applying attendence as {work_mode}")
            log.info(series)
            series = series.to_frame().T
            
            WebDriverWait(self.driver,30).until(EC.presence_of_element_located((By.CSS_SELECTOR,"a#Self-team")))
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
                WebDriverWait(self.driver,30).until(EC.element_to_be_clickable((By.XPATH,"//select[@name='RequestTypeId']/option[@value='Manual Attendance']")))
                self.driver.find_element(By.XPATH,"//select/*[@value='Manual Attendance' and position()=1]").click()
                # SELECT REGULARIZATION TYPE AND HANDLE POP UP ALERT
                log.info("SELECT REGULARIZATION TYPE AND HANDLE POP UP ALERT")
                WebDriverWait(self.driver,30).until(EC.element_to_be_clickable((By.XPATH,"//select[@name='RegularizationType']/option[@value='Working From Home']")))
                self.driver.find_element(By.XPATH,"//select[@name='RegularizationType']/option[@value='Working From Home']").click()
                WebDriverWait(self.driver,30).until(EC.presence_of_element_located((By.CSS_SELECTOR,"div#Common-Error-Alert-Model[aria-hidden='false']")))
                WebDriverWait(self.driver,30).until(EC.element_to_be_clickable((By.XPATH,"//div[@id='Common-Error-Alert-Model' and @aria-hidden='false']/descendant::node()/button")))
                self.driver.find_element(By.XPATH,"//div[@id='Common-Error-Alert-Model' and @aria-hidden='false']/descendant::node()/button").click()
            
            elif "swipe_adjustment" in work_mode:
                # SELECT DROPDOWN OPTION AS SWIPE ADJUSTMENT
                log.info(f"SELECT DROPDOWN OPTION AS SWIPE ADJUSTMENT TYPE:{work_mode}")
                WebDriverWait(self.driver,30).until(EC.visibility_of_element_located((By.XPATH,"//select[@name='RequestTypeId']/option[@value='Swipe Ad']")))
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
            WebDriverWait(self.driver,30).until(EC.presence_of_element_located((By.CSS_SELECTOR,"input#InTime")))
            # in_time_field = self.driver.find_element(By.CSS_SELECTOR,"input#InTime")
            # out_time_field = self.driver.find_element(By.CSS_SELECTOR,"input#OutTime")
            # self.driver.execute_script("arguments[0].setAttribute('value', '14:00')", in_time_field)
            # self.driver.execute_script("arguments[0].setAttribute('value', '23:30')", out_time_field)
            if tags == "AS":
                self.driver.find_element(By.CSS_SELECTOR,"input#InTime").clear()
                self.driver.find_element(By.CSS_SELECTOR,"input#InTime").send_keys("14:00")
                self.driver.find_element(By.CSS_SELECTOR,"input#OutTime").clear()
                self.driver.find_element(By.CSS_SELECTOR,"input#OutTime").send_keys("23:30")
            elif tags == "MS":
                self.driver.find_element(By.CSS_SELECTOR,"input#InTime").clear()
                self.driver.find_element(By.CSS_SELECTOR,"input#InTime").send_keys("06:00")
                self.driver.find_element(By.CSS_SELECTOR,"input#OutTime").clear()
                self.driver.find_element(By.CSS_SELECTOR,"input#OutTime").send_keys("15:30")
            else:
                pass
            self.driver.find_element(By.CSS_SELECTOR,"a#submitRecord").click()
            # HANDLE POP UP ALERT UPON SUBMIT
            log.info("HANDLE POP UP ALERT UPON SUBMIT")
            WebDriverWait(self.driver,30).until(EC.presence_of_element_located((By.CSS_SELECTOR,"div#submit-attendance[aria-hidden='false']")))
            WebDriverWait(self.driver,30).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"button#SaveRecords")))
            self.driver.find_element(By.CSS_SELECTOR,"button#SaveRecords").click()
            # HANDLE POP UP ALERT UPON CONFIRMATION OF SUBMIT
            log.info("HANDLE POP UP ALERT UPON CONFIRMATION OF SUBMIT")
            WebDriverWait(self.driver,30).until(EC.presence_of_element_located((By.CSS_SELECTOR,"div#submit-successfully-attendance[aria-hidden='false']")))
            WebDriverWait(self.driver,30).until(EC.element_to_be_clickable((By.XPATH,"//div[@id='submit-successfully-attendance' and @aria-hidden='false']/descendant::node()/button")))
            self.driver.find_element(By.XPATH,"//div[@id='submit-successfully-attendance' and @aria-hidden='false']/descendant::node()/button").click()
            print(f"Successfully applied attendence for date: {series['Date']}")
            return f'Successful for Date: {series.loc[idx,"Date"]}'
            # return "failed"
        except Exception as e:
            log.setLevel(logging.ERROR)
            log.error(f"Encountered error at attendence.apply_attendance -> {e} \n data: {series} \n type: {work_mode}")
            print(f"Failed to apply attendence for date: {series['Date']}")
            if "https://shiftallowance.in.capgemini.com/AMSAttendanceRequest/SelfAttendance" in self.driver.current_url:                
                WebDriverWait(self.driver,30).until(EC.presence_of_element_located((By.CSS_SELECTOR,"li#liattendance")))
                self.driver.find_element(By.CSS_SELECTOR,"li#liattendance").click()
                self.driver.find_element(By.XPATH,"//ul/li[@id='liattendance']/ul[@class='dropdown-menu']/li/a").click()
            return "Failed"
        
    
def main(cmdargs:list):
    # print("cmdargs from main: ",cmdargs,len(cmdargs))

    if len(cmdargs) > 1:
        # print("Flags entered: ",cmdargs,len(cmdargs))

        if '-i' in cmdargs and '-m' in cmdargs:
            print("interactive with month specified")

            if len(cmdargs) >= indx+1 and re.search("[0-9]",str(cmdargs)) != None:
                print("checking for date -m<month>")
                att = attendence(mode="show",month=int(cmdargs[indx+1]))

            else:
                print("month data not found in -m")
                log.error("Month value not entered")
                print("Month Data not found - \n enter flag like: py -m Attendbot.mark -m 8 -<ADDITional Flag>")
                att = attendence(mode="show")

        elif '-i' in cmdargs:
            exp = re.compile('^.[a-z][0-9]{2}$|^.[a-z][0-9]{1}$')
            repeat_check = [x for x in cmdargs if re.search(exp,x)]
            if len(repeat_check) == 1:
                month = repeat_check[0].split('-m')[1]
                att = attendence(mode="show",month=int(month))
            else:
                print("please enter the flags like so: \n py -m Attendbot.mark -m 8 -<ADDITional Flag> \n ")
                att = attendence(mode="show")                

        elif '-m' in cmdargs:
            indx = cmdargs.index('-m')
            if len(cmdargs) >= indx+1 and re.search("[0-9]",str(cmdargs)) != None:
                print("checking for date -m<month>")
                att = attendence(month=int(cmdargs[indx+1]))

            else:
                print("month data not found in -m")
                log.error("Month value not entered")
                print("Month Data not found - \n enter flag like: py -m Attendbot.mark -m 8 -<ADDITional Flag>")
                att = attendence()
        else:
            print("Operation not supported. \n Enter flag like: \n py -m Attendbot.mark -m 8 -<ADDITional Flag>")
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
    cmdargs = sys.argv
    refresh = updates()
    check = refresh.pull_this()
    print(cmdargs)
    if check:
        update = refresh.update('Attendbot')
        print("\n","\033[34m=\033[37m"*40)
        print("="*40,"\n")
        print("\033[32m  The bot has just been updated \033[37m")
        print("\033[32m  Please rerun the bot with: py -m Attendbot.mark -m 8 -<ADDITional Flag> \033[37m \n")
        print("\033[34m#\033[37m"*40)
    else:
        print("\033[41m Failed to update the Bot \033[40m \n")
        print("\033[34m=\033[37m"*100)
        print("\033[32m Bot will continue to run on the older build. \n The devs are working to fix this! \n In case the issue persists I recommend re-installing the Bot. \n At: https://github.com/Mrunemployed/AttendBot-CG \033[37m \n")
        print("\033[34m=\033[37m"*100)
        main(cmdargs)
    
 