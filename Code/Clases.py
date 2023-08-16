from Code.Funciones import get_value, get_list, get_value_link, get_sub_task, get_child_item, get_po, get_sm, \
    expand_history, get_first_team, get_attribute, get_user_approved, get_files
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
        self.TeamBacklog = get_value(self.Driver, TeamBacklogXpath)
        self.Attachments = get_list(self.Driver, AttachmentsXpath)
        self.Labels = get_list(self.Driver, LabelsXpath)
        self.FeatureLink = get_value_link(self.Driver, FeatureLinkXpath)
        self.PullRequest = get_value_link(self.Driver, PullRequestXpath)
        self.SubTask = get_sub_task(self.Driver)
        self.ChildItem = get_child_item(self.Driver)
        self.TeamBacklogCreated = self.get_team_backlog_history()
        self.PO = get_po(self.TeamBacklogCreated)
        self.SM = get_sm(self.TeamBacklogCreated)
        self.LatestBuildStatus = None
        self.LatestBuildTime = None
        self.UserApproved = None
        self.Files = None
        self.PRLink = None
        self.FeatureProgram = self.get_feature_program()
        self.get_dependency()
        self.get_data_pr()

    def get_team_backlog_history(self):
        team_backlog_list = expand_history(self.Driver)
        if team_backlog_list is not None:
            return get_first_team(team_backlog_list)
        else:
            return self.TeamBacklog

    def get_feature_program(self):
        if self.FeatureLink is not None:
            self.Driver.get(self.FeatureLink[1])
            return [get_list(self.Driver, ProgramIncrementXpath, 2), get_value(self.Driver, StatusXpath)]
        else:
            return

    def get_dependency(self):
        if self.ChildItem is not None:
            feature_list = []
            for Child in self.ChildItem:
                self.Driver.get(Child[1])
                feature_list.append(
                    [get_value_link(self.Driver, FeatureLinkXpath, 5), get_value(self.Driver, TypeXpath)])
            self.ChildItem = [child + feature for child, feature in zip(self.ChildItem, feature_list)]

    def get_data_pr(self):
        if self.PullRequest is not None:
            self.Driver.get(self.PullRequest[1])
            self.PRLink = get_attribute(self.Driver, PRLinkXpath, "href", 5)
            self.Driver.get(self.PRLink+"/overview")
            self.UserApproved = get_user_approved(self.Driver, 5)
            self.Driver.get(self.PRLink+"/diff")
            self.Files = get_files(self.Driver, 4)
            self.Driver.get(self.PRLink+"/builds")
            self.LatestBuildStatus = get_value(self.Driver, LatestBuildStatusXpath, 4)
            self.LatestBuildTime = get_attribute(self.Driver, LatestBuildTimeXpath, "datetime")
