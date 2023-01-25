from dataclasses import dataclass

from fake_useragent import UserAgent
from requests_html import HTML
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


def get_user_agent():
    ua = UserAgent(verify_ssl=False)
    return ua.random


semesters = {
    1: "Осенний семестр {academic_year}",
    2: "Весенний семестр {academic_year}",
}

timetable_types_value = {
    "group": "1",
    "teacher": "2",
    "room": "3",
}

timetable_select_names = {
    "group": "student_group_id",
    "teacher": "teacher",
}


@dataclass
class TimetableScraper:
    """Scrapes the ISU timetable page for a given group and semester."""

    academic_year: str
    semester: int
    group: str = None
    teacher: str = None
    room: str = None
    endpoint: str = "https://isu.ugatu.su/api/new_schedule_api/"
    driver: WebDriver = None
    headless: bool = True

    def __post_init__(self):
        self.driver = self.get_driver()
        self.driver.get(self.endpoint)

    def get_driver(self) -> WebDriver:
        if self.driver is None:
            options = Options()
            if self.headless:
                options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument(f'user-agent={get_user_agent()}')
            self.driver = webdriver.Chrome(options=options)
        return self.driver

    def _submit_form(self) -> None:
        form = self.driver.find_element(By.TAG_NAME, "form")
        form.submit()

    def select_semester(self) -> None:
        semester_select = self.driver.find_element(By.NAME,
                                                   "schedule_semestr_id")
        semester_str = semesters[self.semester].format(
            academic_year=self.academic_year)
        for term in semester_select.find_elements(By.TAG_NAME, "option"):
            if term.text == semester_str:
                term.click()
                break

    # def select_group(self) -> None:
    #     group_value = timetable_types_value["group"]
    #     group_filter_radio = self.driver.find_element(
    #         By.CSS_SELECTOR, f"input[value='{group_value}']")
    #     group_filter_radio.click()
    #     self._submit_form()
    #     group_select = self.driver.find_element(
    #         By.CSS_SELECTOR, "select[name='student_group_id']")
    #     for group in group_select.find_elements(By.TAG_NAME, "option"):
    #         if self.group.lower() in group.text.lower():
    #             group.click()
    #             break
    #     else:
    #         raise ValueError(f"Group {self.group} not found.")

    # def select_teacher(self) -> None:
    #     teacher_value = timetable_types_value["teacher"]
    #     teacher_filter_radio = self.driver.find_element(
    #         By.CSS_SELECTOR, f"input[value='{teacher_value}']")
    #     teacher_filter_radio.click()
    #     self._submit_form()
    #     teacher_select = self.driver.find_element(By.CSS_SELECTOR,
    #                                               "select[name='teacher']")
    #     for teacher in teacher_select.find_elements(By.TAG_NAME, "option"):
    #         if self.teacher.lower() in teacher.text.lower():
    #             teacher.click()
    #             break
    #     else:
    #         raise ValueError(f"Teacher {self.teacher} not found.")

    def select_timetable_type(self) -> None:
        """Selects the timetable type (group, teacher)"""
        if self.group and self.teacher or self.group and self.room or self.teacher and self.room:
            raise ValueError(
                "Only one of group, teacher or room can be specified.")
        elif not self.group and not self.teacher and not self.room:
            raise ValueError(
                "One of group, teacher or room must be specified.")

        if self.group:
            timetable_value = timetable_types_value["group"]
            select_name = timetable_select_names["group"]
        elif self.teacher:
            timetable_value = timetable_types_value["teacher"]
            select_name = timetable_select_names["teacher"]
        filter_radio = self.driver.find_element(
            By.CSS_SELECTOR, f"input[value='{timetable_value}']")
        filter_radio.click()
        self._submit_form()
        select = self.driver.find_element(By.CSS_SELECTOR,
                                          f"select[name='{select_name}']")
        for option in select.find_elements(By.TAG_NAME, "option"):
            if self.group and self.group.lower() in option.text.lower():
                option.click()
                break
            elif self.teacher and self.teacher.lower() in option.text.lower():
                option.click()
                break
        else:
            raise ValueError(
                f"Timetable for {self.group or self.teacher} not found.")

        # TODO: implement room selection

    def html_object(self) -> HTML:
        self.select_semester()
        self.select_timetable_type()
        self._submit_form()
        return HTML(html=self.driver.page_source)

    def get_timetables_dict(self) -> dict:
        html = self.html_object()
        timetable_table = html.find("table", first=True)
        if not timetable_table:
            raise ValueError("No timetable found.")

        table_header = timetable_table.find("thead", first=True)
        headers = []
        for td in table_header.find("td"):
            headers.append(td.text)

        timetables_dict = {}
        table_body = timetable_table.find("tbody", first=True)
        for row in table_body.find("tr"):
            cells = row.find("td")
            if len(cells) == 1:
                day = cells[0].text
                timetables_dict[day] = []
            else:
                timetable = {}
                for header, cell in zip(headers[1:], cells):
                    timetable[header] = cell.text
                timetables_dict[day].append(timetable)
        return timetables_dict