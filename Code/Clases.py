from Code.Funciones import *
from Code.Constantes import *


class ValidHut:
    def __init__(self, driver):
        self.Driver = driver
        self.KeyVal = get_value(self.Driver, KeyValXpath, 3)
        self.Summary = get_value(self.Driver, SummaryXpath)
        self.Assignee = get_value(self.Driver, AssigneeXpath)
        self.Reporter = get_value(self.Driver, ReporterXpath)
        self.Type = get_value(self.Driver, TypeXpath)
        self.Status = get_value(self.Driver, StatusXpath)
        self.AcceptanceCriteria = get_value(self.Driver, AcceptanceCriteriaXpath)
        self.ItemType = get_value(self.Driver, ItemTypeXpath)
        self.TechStack = get_value(self.Driver, TechStackXpath)
        self.Attachments = get_list(self.Driver, AttachmentsXpath)
        self.Labels = get_list(self.Driver, LabelsXpath)
        self.FeatureLink = get_value_link(self.Driver, FeatureLinkXpath)
        self.PullRequest = get_value_link(self.Driver, PullRequestXpath)
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
                feature_list.append(get_value_link(self.Driver, FeatureLinkXpath, 5))
            self.ChildItem = [child + [feature] for child, feature in zip(self.ChildItem, feature_list)]

    def get_data_pr(self):
        if self.PullRequest is not None:
            self.Driver.get(self.PullRequest[1])
            pr_link = get_attribute(self.Driver, PRLinkXpath, "href", 5)
            self.Driver.get(pr_link+"/overview")
            self.UserApproved = get_user_approved(self.Driver, 5)
            self.Driver.get(pr_link+"/diff")
            self.Files = get_files(self.Driver, 4)
            self.Driver.get(pr_link+"/builds")
            self.LatestBuildStatus = get_value(self.Driver, LatestBuildStatusXpath, 4)
            self.LatestBuildTime = get_attribute(self.Driver, LatestBuildTimeXpath, "datetime")
