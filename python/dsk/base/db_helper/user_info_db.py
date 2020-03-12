from pprint import pformat
from dsk.base.tdata.gen_tree import GenTree


class UserListInfoDb(GenTree):

    def __init__(self):
        super(UserListInfoDb, self).__init__()


class UserInfoDb(GenTree):
    UF = ['login','firstname','lastname','permission_rule_set','email']
    All_Groups = ['Artist','Supervisor','ProductionPlus',
                  'Production','Admin','TD','Dev','InOut','Client','Boss']


    def __init__(self):
        super(UserInfoDb, self).__init__()
        self.reset()

    def reset(self):
        self.id = -1
        self.firstname = ""
        self.lastname = ""

    def setdata(self, arg):

        login = arg.get('login',"")
        if login != "":
            self.setName(login)

            self.id = arg.get('id')
            self.permission_rule_set = arg.get('permission_rule_set')

            firstname = arg.get('firstname')
            try:
                self.firstname = firstname.decode('unicode_escape').encode('ascii','ignore')
            except:
                pass
            lastname = arg.get('lastname')
            try:
                self.lastname = lastname.decode('unicode_escape').encode('ascii','ignore')
            except:
                pass
            self.email = arg.get('email')
            return True

        return False


    def is_same_user(self, first_and_last):
        """Sometime the first name and last name got reversed"""
        first_and_last = first_and_last.decode('unicode_escape').encode('ascii','ignore')
        if first_and_last == "%s %s" % (self.firstname,self.lastname):
            return True
        if first_and_last == "%s %s" % (self.lastname,self.firstname):
            return True
        return False

    def is_artist(self):
        #name == "Artist"
        return self.permission_rule_set['id'] == 8

    def is_supervisor(self):
        #name == "Supervisor"
        return self.permission_rule_set['id'] == 13

    def is_production_plus(self):
        #ProductionPlus
        return self.permission_rule_set['id'] == 24

    def is_production(self):
        # Production
        return self.permission_rule_set['id'] == 19

    def is_admin(self):
        #Admin
        return self.permission_rule_set['id'] == 5

    def is_td(self):
        #TD
        return self.permission_rule_set['id'] == 22

    def is_dev(self):
        #Dev
        return self.permission_rule_set['id'] == 20

    def is_in_out(self):
        #InOut
        return self.permission_rule_set['id'] == 18

    def is_client(self):
        #Client
        return self.permission_rule_set['id'] == 14

    def is_boss(self):
        #Boss
        return self.permission_rule_set['id'] == 23

    def get_permission_group(self):
        return self.permission_rule_set['name']

    def get_permission_id_group(self):
        return self.permission_rule_set['id']

    def get_user_dict(self):
        return {'name': "%s %s" % (self.firstname, self.lastname),
                'type': "HumanUser",
                'id': self.id}


    @classmethod
    def all_groups(cls):
        return cls.All_Groups

    def __repr__(self):
        return pformat(self.__dict__)
