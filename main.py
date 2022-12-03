from random import randint, shuffle
from tkinter import Tk, BOTH, IntVar, LEFT
from tkinter.ttk import Frame, Label, Scale, Style

PLAYER_ACTIVE = True
EVENT_ACTIVE = False
EVENT_CHANCE = 10
N_BANK = 100
N_TERMS = 5


class Scaling_window(Frame):

    def __init__(self, st, minval, maxval):
        super().__init__()

        self.minv = minval
        self.maxv = maxval
        self.initUI(st)

    def initUI(self, st):
        self.master.title("ROR/ROD")
        self.style = Style()
        self.style.theme_use("default")
        self.st = st
        self.pack(fill = BOTH, expand = 1)

        scale = Scale(self, from_ = self.minv, to = self.maxv, command = self.onScale)
        scale.pack(side = LEFT, padx = 15)

        self.var = IntVar()
        self.label = Label(self, text = self.st, textvariable = self.var)
        self.label.pack(side = LEFT)

    def onScale(self, val):
        v = int(float(val))
        self.var.set(v)


class Event:
    def __init__(self, param, cost, minv, maxv, quest_line, ans, resp_Y, resp_N, res_negative, res_positive):
        self.param, self.cost, self.minv, self.maxv, self.quest_line, self.ans, self.resp_Y, self.resp_N, = param, cost, minv, maxv, quest_line, ans, resp_Y, resp_N,
        self.res_negative, self.res_positive = res_negative, res_positive

    def playeventManagableCost(self, num):
        if input(self.quest_line) == self.ans:
            print(self.resp_Y)
            CentralBank.banks[num].reserves -= self.cost
            if randint(0, 100) > 50:
                res = self.minv + (self.maxv - self.minv) * (randint(100) / 100)
                CentralBank.global_awareness -= res
                print(self.res_positive.format(res))
            else:
                print(self.res_negative.format(res))
        else:
            print(self.resp_N)

    def playeventManagableAwareness(self, num):
        if input(self.quest_line) == self.ans:
            print(self.resp_Y)
            CentralBank.global_awareness += self.cost
            if randint(0, 100) > 50:
                res = self.minv + (self.maxv - self.minv) * (randint(100) / 100)
                CentralBank.banks[q] += res
                print(self.res_positive.format(res))
            else:
                print(self.res_negative)
        else:
            print(self.resp_N)
        # " в результате инвестиций было получено {0} рублей "

    def playeventUnmanagableCost(self, num):
        CentralBank.banks[num].investments -= self.cost
        print(self.quest_line)
        res = self.minv + (self.maxv - self.minv) * (randint(100) / 100)
        CentralBank.global_awareness += res
        print(self.res_positive.format(res))

    def playeventUnmanagableAwareness(self, num):
        CentralBank.global_awareness += self.cost
        print(self.quest_line)
        res = (self.minv + (self.maxv - self.minv) * (randint(100) / 100))
        CentralBank.banks[num].investments += res
        print(self.res_positive.format(res))


class CentralBank:
    rate_on_reserves = 0.1
    banks = []
    EventsUnman = []
    EventsMan = []
    bankruptBanks = []
    bankruptInvestors = []
    droppedInvestors = []
    global_awareness = 1
    inflation = 0.1

    @staticmethod
    def count_gains():
        investors_gain = 0
        banks_gain = 0
        for i in CentralBank.bankruptInvestors:
            investors_gain += i.gain
        for i in CentralBank.bankruptBanks:
            banks_gain += i.gain
        for i in CentralBank.droppedInvestors:
            investors_gain += i.gain
        for i in CentralBank.banks:
            banks_gain += i.reserve + i.investments
        return banks_gain, investors_gain


class Bank:
    default_value_sum = 212 * (10 ** 6)
    default_investors_count = 2 * (10 ** 3)

    def __init__(self, ror):
        self.term_sur = 0
        self.investors = []
        s = Bank.default_value_sum
        self.rate_on_reserves = ror
        self.reserve = s * ror
        self.investments = s * (1 - ror)
        self.rate_on_depo = CentralBank.inflation
        self.gain = 0
        prev_i = 0
        for i in range(Bank.default_investors_count):
            i = prev_i + round(randint(round(1), round(7)) / 10000, 4)
            newval = round(s * (i - prev_i), 2)
            self.investors.append(Investor(newval))
            s -= newval
            prev_i = round(i, 4)

    def dropDepos(self):
        for i, inv in enumerate(self.investors):
            inv.awareness = inv.awareness_count(self)
            if inv.awareness > randint(50, 100):

                self.reserve -= inv.deposit
                self.investors[i].gain = inv.deposit
                CentralBank.droppedInvestors.append(self.investors[i])
                self.investors.pop(i)
                if self.reserve < 0:
                    self.bankrupt()
                    return True
        return False

    def bankrupt(self):
        for i, inv in enumerate(self.investors):
            inv.gain = -100
            CentralBank.bankruptInvestors.append(self.investors[i])
        CentralBank.global_awareness = min(100, randint(CentralBank.global_awareness, CentralBank.global_awareness + 5))
        CentralBank.bankruptBanks.append(self)
        return True


class Investor:
    def __init__(self, depo):
        self.deposit = depo
        self.awareness = 1
        self.gain = 0

    def __repr__(self):
        return str(self.deposit)

    def __ge__(self, other):
        return self.deposit >= other.deposit

    def __lt__(self, other):
        return self.deposit < other.deposit

    def __eq__(self, other):
        return self.deposit == other.deposit

    def addDepo(self, depo):
        self.deposit += depo

    def awareness_count(self, bank):
        return self.deposit / (
                Bank.default_value_sum / Bank.default_investors_count) * CentralBank.inflation * (
                       (CentralBank.global_awareness) / 100) / bank.rate_on_depo


def initWorld():
    Bank.banks = []
    for i in range(N_BANK):
        b = Bank((randint(int(CentralBank.rate_on_reserves * 100), 100) / 100))
        CentralBank.banks.append(b)
    CentralBank.banks.pop(0)
    CentralBank.banks.append(Bank(randint(int(CentralBank.rate_on_reserves * 100), 100) / 100))
    CentralBank.banks[N_BANK - 1].rate_od_depo = CentralBank.inflation * 2

    global PLAYER_BANK
    PLAYER_BANK = N_BANK - 1
    for b in CentralBank.banks:
        b.investors = sorted(b.investors)
        s = 0
        for i in b.investors:
            s += i.deposit
        b.investors[0].addDepo((Bank.default_value_sum - s) / 3)
        b.investors[1].addDepo((Bank.default_value_sum - s) / 3)
        b.investors[2].addDepo((Bank.default_value_sum - s) / 3)
        b.investors = sorted(b.investors, reverse = True)
        # print(min(b.investors))
    CentralBank.EventsMan.append(
        Event(1, 10000, 0.2, 0.3, 'вы можете инвестировать в детский сад', 'Y', 'инвиситиции приняты',
              'инвестиции неприняты', 'позитивный', 'негативный'))
    CentralBank.EventsMan.append(
        Event(1, -5000, -0.6, -0.4, 'у вас есть возможность продать свои акции за 5000', 'Y', ' принято', 'непринято',
              'позитивный', 'негативный'))
    CentralBank.EventsMan.append(
        Event(1, 4356, 0.4, 0.56, 'вы можете купить акции за 4356 ', 'Y', 'принято', 'непринято', 'позитивный',
              'негативный'))
    CentralBank.EventsMan.append(
        Event(1, 11234, 0.76, 0.12, 'вы можете продать свои ценные бумаги за 11234', 'Y', 'принято', 'непринято',
              'позитивный', 'негативный'))


def main():
    root = Tk()
    ROR_scale = Scaling_window("ROR", CentralBank.rate_on_reserves, 100)
    ROD_scale = Scaling_window("ROD", 1, 100)
    root.geometry("250x100+300+300")
    root.mainloop()
    initWorld()  # инициализация
    for term in range(N_TERMS):
        CentralBank.inflation += 0.1  # рост инфляции каждый "цикл"
        for q, bank in enumerate(CentralBank.banks):
            CentralBank.banks[q].term_sur += 1
            if EVENT_ACTIVE and q == PLAYER_BANK:
                CentralBank.EventsMan = shuffle(CentralBank.EventsMan)
                for event in CentralBank.EventsMan:
                    if randint(0, 100) < EVENT_CHANCE:
                        if event.param == 1:
                            event.playeventManagableCost(q)
                        else:
                            event.playeventManagableAwareness(q)
                CentralBank.EventsUnmman = shuffle(CentralBank.EventsUnman)
                for event in CentralBank.EventsUnman:
                    if randint(0, 100) < EVENT_CHANCE:
                        if event.param == 1:
                            event.playeventUnmanagableCost(q)
                        else:
                            event.playeventUnmanagableAwareness(q)
            if q == PLAYER_BANK and PLAYER_ACTIVE:
                CentralBank.banks[q].rate_on_reserves = float(int(ROR_scale.var.get()) / 100)
                CentralBank.banks[q].rate_on_depo = float(int(ROD_scale.var.get()) / 100)
                root = Tk()
                ROR_scale = Scaling_window("ROR", CentralBank.rate_on_reserves, 100)
                ROD_scale = Scaling_window("ROD", 1, 100)
                root.geometry("250x100+300+300")
                root.mainloop()
                print("In ", term, " term player has chosen RoR and RoD: ", CentralBank.banks[q].rate_on_reserves,
                      CentralBank.banks[q].rate_on_depo)

            if bank.dropDepos():  # если банк обанкротился
                for inv in bank.investors:
                    CentralBank.banks[q].gain -= inv.deposit
                CentralBank.banks.pop(q)
            else:
                for i, inv in enumerate(bank.investors):
                    CentralBank.banks[q].reserve -= inv.deposit * bank.rate_on_depo  # выплачиваем проценты вкладчикам
                    CentralBank.banks[q].investors[i].deposit *= (bank.rate_on_depo + 1)
                    CentralBank.banks[q].investors[i].deposit /= (CentralBank.inflation + 1)
                CentralBank.banks[q].investments *= randint(5, 15) / 10
                s = CentralBank.banks[q].reserve + CentralBank.banks[q].investments  # все активы банка
                s /= (CentralBank.inflation + 1)
                CentralBank.banks[q].reserve, CentralBank.banks[q].investments = s * bank.rate_on_reserves, s * (
                        1 - bank.rate_on_reserves)  # пересчитываем капитал банка (собрали все деньги и поделили по ставке)

    print("gains", CentralBank.count_gains())
    for bank in CentralBank.banks:
        print(bank.rate_on_reserves, len(bank.investors))

    print(len(CentralBank.banks))

    for bank in CentralBank.bankruptBanks:
        print(bank.rate_on_reserves, len(bank.investors))

    print(len(CentralBank.bankruptBanks))


if __name__ == '__main__':
    main()
