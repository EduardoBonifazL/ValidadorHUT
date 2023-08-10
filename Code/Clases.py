from Code.Funciones import *


class ValidHut:
    def __init__(self, driver):
        self.Driver = driver
        self.KeyVal = get_value(self.Driver, '//*[@id="key-val"]', 3)
        self.Summary = get_value(self.Driver, '//*[@id="summary-val"]')
        self.Assignee = get_value(self.Driver, '//dt[@title="Assignee"]/following-sibling::dd/span')
        self.Reporter = get_value(self.Driver, '//dt[@title="Reporter"]/following-sibling::dd/span')
        self.Type = get_value(self.Driver, '//*[@id="type-val"]')
        self.Status = get_value(self.Driver, '//*[@id="status-val"]/span')
        self.AcceptanceCriteria = get_value(self.Driver, '//*[@id="field-customfield_10260"]/div[1]/div/p')
        self.ItemType = get_value(self.Driver, '//*[@id="customfield_10270-val"]')
        self.TechStack = get_value(self.Driver, '//*[@id="customfield_18001-val"]')
        self.Attachments = get_list(self.Driver, '//*[@id="attachment_thumbnails"]/li/dl/dt/a')
        self.Labels = get_list(self.Driver, '//strong[@title="Labels"]/following-sibling::div/ul[@class="labels"]/li')
        self.FeatureLink = get_value_link(self.Driver, '//strong[@title="Feature Link"]/following-sibling::div/a')
        self.PullRequest = get_value_link(self.Driver, '//*[@id="pullrequest-status-panel"]/dl/dt/div/div/div/a')
        self.SubTask = get_sub_task(self.Driver)
        self.ChildItem = get_child_item(self.Driver)
        self.LatestBuildStatus = None
        self.LatestBuildTime = None
        self.UserApproved = None
        self.Files = None
        self.get_dependency()
        self.get_data_pr()

    def get_dependency(self):
        if self.ChildItem is not None:
            feature_list = []
            for Child in self.ChildItem:
                self.Driver.get(Child[1])
                feature_list.append(get_value_link(self.Driver, '//strong[@title="Feature Link"]/following-sibling::div/a', 7))
            self.ChildItem = [child + [feature] for child, feature in zip(self.ChildItem, feature_list)]

    def get_data_pr(self):
        if self.PullRequest is not None:
            self.Driver.get(self.PullRequest[1])
            pr_link = get_attribute(self.Driver, '//tr[@class="pullrequest-row"]/td[@class="title"]/a', "href", 7)
            self.Driver.get(pr_link+"/overview")
            self.UserApproved = get_user_approved(self.Driver, 7)
            self.Driver.get(pr_link+"/diff")
            self.Files = get_files(self.Driver, 4)
            self.Driver.get(pr_link+"/builds")
            self.LatestBuildStatus = get_value(
                self.Driver,
                '//td[div/div/div/span/span/text()="Latest"]/following-sibling::td[@class="build-row-status"]/div/div/div',
                4
            )
            self.LatestBuildTime = get_attribute(
                self.Driver,
                '//td[div/div/div/span/span/text()="Latest"]/following-sibling::td[@class="build-row-time"]/div/span/time',
                "datetime"
            )

    def validar_hut(self):
        pass
