KeyValXpath = '//*[@id="key-val"]'
SummaryXpath = '//*[@id="summary-val"]'
AssigneeXpath = '//dt[@title="Assignee"]/following-sibling::dd/span'
ReporterXpath = '//dt[@title="Reporter"]/following-sibling::dd/span'
TypeXpath = '//*[@id="type-val"]'
StatusXpath = '//*[@id="status-val"]/span'
AcceptanceCriteriaXpath = '//*[@id="field-customfield_10260"]/div[1]/div/p'
ItemTypeXpath = '//*[@id="customfield_10270-val"]'
TechStackXpath = '//*[@id="customfield_18001-val"]'
AttachmentsXpath = '//*[@id="attachment_thumbnails"]/li/dl/dt/a'
LabelsXpath = '//strong[@title="Labels"]/following-sibling::div/ul[@class="labels"]/li'
FeatureLinkXpath = '//strong[@title="Feature Link"]/following-sibling::div/a'
PullRequestXpath = '//*[@id="pullrequest-status-panel"]/dl/dt/div/div/div/a'
PRLinkXpath = '//tr[@class="pullrequest-row"]/td[@class="title"]/a'
LatestLabel = '//td[div/div/div/span/span/text()="Latest"]'
LatestBuildStatusXpath = f'{LatestLabel}/following-sibling::td[@class="build-row-status"]/div/div/div'
LatestBuildTimeXpath = f'{LatestLabel}/following-sibling::td[@class="build-row-time"]/div/span/time'
Approved = '@class="activity-item approved-activity"'
Unapproved = '@class="activity-item unapproved-activity"'
Reviewed = '@class="activity-item reviewed-activity"'
UserViewXpath = f'//div[{Approved} or {Unapproved} or {Reviewed}]//span[@class="user-name"]'
UserStatusXpath = f'//div[{Approved} or {Unapproved} or {Reviewed}]//span[@class="lozenge-wrapper"]'
FolderClosedXpath = '//span[@class="aui-icon aui-icon-small icon-folder-closed directory-icon"]'
FileAdded = '@class="aui-icon aui-icon-small icon-file-added status-icon"'
FileMoved = '@class="aui-icon aui-icon-small icon-file-moved status-icon"'
FileModified = '@class="aui-icon aui-icon-small icon-file-modified status-icon"'
FileCopied = '@class="aui-icon aui-icon-small icon-file-copied status-icon"'
FileXpath = f'//a[span[{FileAdded} or {FileMoved} or {FileModified} or {FileCopied}]]'
FileSegmentXpath = '//span[@class="file-breadcrumbs-segment-highlighted"]'
FileSourceXpath = '//a[@aria-label="View the entire source for this file"]'
FileBodyXpath = '/html/body/pre'
