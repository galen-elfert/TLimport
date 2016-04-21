import ConfigParser
from testlink import TestlinkAPIClient, TestLinkHelper, testlinkerrors
import npyscreen
from time import sleep
import os

def walkToTree(path, node):
    """
    Convert an os.walk object into an npyscreen TreeData node tree, recursively
    """
    contents = os.listdir(path)
    for item in contents:
        thisPath = os.path.join(path, item)
        content = {'path':path, 'name':item}
        if os.path.isdir(thisPath):
            content.update({'type':'folder'})
            child = node.new_child(content=content)
            walkToTree(thisPath, child)
        elif os.path.isfile(thisPath) and not os.path.islink(thisPath):
            content.update({'type':'file'})
            node.new_child(content=content)


class configForm(npyscreen.Form):
    def afterEditing(self):
        self.parentApp.host = self.hostBox.value
        self.parentApp.devkey = self.devkeyBox.value
        try:
            self.statusBox.value = 'Connecting...'
            tlh = TestLinkHelper(server_url='http://'+self.parentApp.host+'/lib/api/xmlrpc/v1/xmlrpc.php', devkey=self.parentApp.devkey)
            self.parentApp.tl = tlh.connect(TestlinkAPIClient)
            self.parentApp.tl.sayHello()
        except testlinkerrors.TLConnectionError as err:
            self.statusBox.value = err
        else:
            self.parentApp.setNextForm('IMPORT')

    def create(self):
        self.hostBox = self.add(npyscreen.TitleText, name='Host', value=self.parentApp.host)
        self.devkeyBox = self.add(npyscreen.TitleText, name='DevKey', value=self.parentApp.devkey)
        self.statusBox = self.add(npyscreen.FixedText, name='Status', value='')


class importForm(npyscreen.Form):
    def afterEditing(self):
        self.parentApp.setNextForm(None)

    def create(self):
        self.localTreeData = npyscreen.TreeData()
        walkToTree('.', self.localTreeData)
        self.localTree = self.add(npyscreen.MLTreeMultiSelect, name='Local Tree', value=self.localTreeData)


class App(npyscreen.NPSAppManaged):
    def onStart(self):
        self.host = '10.1.2.184'
        self.devkey = 'ecdc27095d3877cafea7ae788ca0f23e'
        self.addForm('MAIN', configForm)
        self.addForm('IMPORT', importForm)

if __name__ == '__main__':
    TestApp = App().run()
