import methods


class Scenario(methods.Methods):

    def scenario1(self):
        self._create_server('name0')
        self._create_server('name1')
        self._create_server('name2')
        self._create_server('name3')
        self._create_server('name4')
        self._create_server('name5')
        self._create_server('name6')
        self._create_server('name7')
        self._create_server('name8')
        self._create_server('name9')

if __name__ == '__main__':
    qwe = Scenario()
    qwe.scenario1()
