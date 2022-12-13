"""
Case GAME (04.12.2022) By Developers:
Pichuev D. 90 %
Trushkin N. 40 %
#Place  for your ads#
"""
from random import randint, shuffle
from tkinter import Tk, BOTH, IntVar, LEFT
from tkinter.ttk import Frame, Label, Scale, Style, Button

PLAYER_ACTIVE = True
EVENT_ACTIVE = True
EVENT_CHANCE = 10
N_BANK = 100
N_TERMS = 20


class Scaling_window(Frame):
    """interface class"""
    def __init__(self, st, minval, maxval):
        super().__init__()

        self.minv = minval
        self.maxv = maxval
        self.initUI(st)

    def initUI(self, st):
        self.style = Style()
        self.style.theme_use("default")
        self.st = st
        self.pack(fill = BOTH, expand = 1)

        scale = Scale(self, from_ = self.minv, to = self.maxv, command = self.onScale)
        scale.pack(side = LEFT, padx = 15)

        self.var = IntVar()
        self.label = Label(self, text = self.st, textvariable = self.var)
        self.label.pack(side = LEFT)

        Button(self, text = st.split("/")[1], command = self.quit).pack()

    def quit(self):
        self.destroy()

    def onScale(self, val):
        v = int(float(val))
        self.var.set(v)


class Event:
    """Event class"""
    def __init__(self, param, cost, minv, maxv, quest_line, ans, resp_Y, resp_N, res_positive, res_negative):
        self.param, self.cost, self.minv, self.maxv, self.quest_line, self.ans, self.resp_Y, self.resp_N, = param, cost, minv, maxv, quest_line, ans, resp_Y, resp_N,
        self.res_negative, self.res_positive = res_negative, res_positive

    def playeventManagableCost(self, num):
        if input(self.quest_line) == self.ans:
            print(self.resp_Y)
            CentralBank.banks[num].reserve -= self.cost
            if randint(0, 100) > 30:
                res = self.minv + (self.maxv - self.minv) * (randint(0, 100) / 100)
                CentralBank.global_awareness = min(0, CentralBank.global_awareness - res)
                print(self.res_positive, round((float(abs(res)) * 100), 2) * 100, "%")
            else:
                print(self.res_negative)
        else:
            print(self.resp_N)

    def playeventManagableAwareness(self, num):
        if input(self.quest_line) == self.ans:
            print(self.resp_Y)
            CentralBank.global_awareness += self.cost
            if randint(0, 100) > 30:
                res = self.minv + (self.maxv - self.minv) * (randint(100) / 100)
                CentralBank.banks[num] += res
                print(self.res_positive, res)
            else:
                print(self.res_negative)
        else:
            print(self.resp_N)
        # " в результате инвестиций было получено {0} рублей "

    def playeventUnmanagableCost(self, num):
        CentralBank.banks[num].reserve -= self.cost
        print(self.quest_line)
        res = self.minv + (self.maxv - self.minv) * (randint(0,100) / 100)
        CentralBank.global_awareness = min(0, CentralBank.global_awareness - res)
        print(self.res_positive, round((float(abs(res)) * 100),2),"%")

    def playeventUnmanagableAwareness(self, num):
        CentralBank.global_awareness += self.cost
        print(self.quest_line)
        res = (self.minv + (self.maxv - self.minv) * (randint(0,100) / 100))
        CentralBank.banks[num].investments += res
        print(self.res_positive, "%")


class CentralBank:
    """Main Management Class"""
    rate_on_reserves = 0.3
    banks = []
    EventsUnman = []
    EventsMan = []
    bankruptBanks = []
    bankruptInvestors = []
    droppedInvestors = []
    global_awareness = 0.40
    inflation = 0.1

    @staticmethod
    def statestatus():
        """creating status report for player"""
        return (
                "Инфляция на рынке %s, Глобальный уровень тревожности %s \n Общее число банков на рынке: %s. Общее число банков-банкротов %s\n" % (
            (str(round(CentralBank.inflation * 100, 2)) + "%"),
            (str(round(CentralBank.global_awareness * 100, 2)) + "%"), len(CentralBank.banks),
            len(CentralBank.bankruptBanks)))

    @staticmethod
    def count_gains():
        """Counting gains from the game"""
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

        if PLAYER_ACTIVE:
            print("Счёт игрока: ", CentralBank.banks[0].reserve + CentralBank.banks[0].investments)
        return banks_gain, investors_gain


class Bank:
    """Bank player class"""
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

        count_dropped_inv = 0
        count_droped_depos = 0
        for i, inv in enumerate(self.investors):
            inv.awareness = inv.awareness_count(self)
            if inv.awareness > randint(50, 100):

                self.reserve -= inv.deposit
                self.investors[i].gain += inv.deposit
                CentralBank.droppedInvestors.append(self.investors[i])
                self.investors.pop(i)
                count_dropped_inv += 1
                count_droped_depos += inv.deposit
                if self.reserve <= 0:
                    self.bankrupt()
                    return True, count_dropped_inv, count_droped_depos
        return False, count_dropped_inv, count_droped_depos

    def bankrupt(self):
        for i, inv in enumerate(self.investors):
            inv.gain = -100
            CentralBank.bankruptInvestors.append(self.investors[i])
        CentralBank.global_awareness = min(100 / 100, randint(int(CentralBank.global_awareness * 100),
                                                              int(CentralBank.global_awareness * 110)) / 100)
        CentralBank.bankruptBanks.append(self)
        return True


class Investor:
    """Investor player class"""
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
                   (CentralBank.global_awareness)) / bank.rate_on_depo


def initWorld():
    """init function"""
    CentralBank.banks = []
    CentralBank.EventsUnman = []
    CentralBank.EventsMan = []
    CentralBank.bankruptBanks = []
    CentralBank.bankruptInvestors = []
    CentralBank.droppedInvestors = []
    CentralBank.global_awareness = 0.40
    CentralBank.inflation = 0.1

    CentralBank.banks = []
    for i in range(N_BANK):
        b = Bank((randint(int(CentralBank.rate_on_reserves * 100), 100) / 100))
        CentralBank.banks.append(b)
    CentralBank.banks[0].rate_od_depo = CentralBank.inflation * 2
    global PLAYER_BANK_N
    PLAYER_BANK_N = 0
    for b in CentralBank.banks:
        b.investors = sorted(b.investors)
        s = 0
        for i in b.investors:
            s += i.deposit
        b.investors[0].addDepo((Bank.default_value_sum - s) / 3)
        b.investors[1].addDepo((Bank.default_value_sum - s) / 3)
        b.investors[2].addDepo((Bank.default_value_sum - s) / 3)
        b.investors = sorted(b.investors, reverse = True)
    """Event declaration below"""
    CentralBank.EventsMan.append(
        Event(1, 10000, 0.2, 0.3, 'Вы можете инвестировать 10000 рублей в детский сад Y/N', 'Y', 'инвеситиции приняты',
              'инвестиции не приняты', 'Вы повысили доверие людей к  банковской системе на ', 'Реакции не последовало'))
    CentralBank.EventsMan.append(
        Event(1, -5000, -0.6, -0.4, 'У вас есть возможность продать свои акции за 5000 Y/N', 'Y', ' акции проданы',
              'акции не проданы', 'Вы понизили доверие к банковской системе на ', 'Реакции не последовало'))
    CentralBank.EventsMan.append(
        Event(1, 4356, 0.04, 0.05, 'Вы можете купить акции за 4356 Y/N', 'Y', 'вы купили акции', 'акции не куплены',
              'вы купили акции и повысили надежность системы на ', 'Реакции на покупку не последовало'))
    CentralBank.EventsMan.append(
        Event(1, -11234, -0.7, -0.1, 'Вы можете продать свои ценные бумаги за 11234 Y/N', 'Y', 'бумаги проданы',
              'бумаги не проданы', 'Вы продали свои бумаги понизив надежность банковской системы на ',
              'Реакции не последовало'))
    CentralBank.EventsMan.append(
        Event(1, 3600, 0.56, 0.78, 'Вы можете инвесттировать 3600 рублей в больницы Y/N', 'Y', 'инвеситиции приняты',
              'инвестиции не приняты', 'Вы повысили доверие людей к банковской системе на ', 'Реакции не последовало'))
    CentralBank.EventsMan.append(
        Event(1, 7800, 0.34, 0.67, 'вы можете инвестировать 7800 рублей в продукт "Coca-cola" Y/N', 'Y',
              'инвеситиции приняты', 'инвестиции не приняты', 'Вы повысили доверие людей к банковской системе на ',
              'Реакции не последовало'))
    CentralBank.EventsMan.append(
        Event(1, 5688, 0.45, 0.98, 'Вы можете инвестировать 5688 рублей в "Газпром" Y/N', 'Y', 'инвеситиции приняты',
              'инвестиции неприняты', 'Вы повысили доверие людей к банковской системе на ', 'Реакции не последовало'))
    CentralBank.EventsMan.append(
        Event(1, 6778, 0.19, 0.02, 'Вы можете купить акции за 6778 Y/N', 'Y', 'вы купили акции', 'акции не куплены',
              'вы купили акции и повысили надежность системы на ', 'Реакции на покупку не последовало'))
    CentralBank.EventsMan.append(
        Event(1, -3000, -0.76, -0.12, 'Вы можете продать свои ценные бумаги за 3000 Y/N', 'Y', 'бумаги проданы',
              'бумаги  не проданы',
              'Вы понизили доверие людей к банковской системе на', 'Реакции не последовало'))
    CentralBank.EventsMan.append(
        Event(1, -6789, -0.06, -0.72, 'Вы можете продать свои ценные бумаги за 6789 Y/N', 'Y', 'бумаги проданы',
              'бумаги не проданы',
              'Вы понизили доверие людей к банковской системе на', 'Реакции не последовало'))
    CentralBank.EventsMan.append(
        Event(1, -4069, -0.78, -0.38, 'у вас есть возможность продать свои акции за 4060 Y/N', 'Y', 'бумаги проданы',
              'бумаги  не проданы', 'Вы понизили доверие людей к банковской системе на', 'Реакции не последовало'))

    CentralBank.EventsUnman.append(
        Event(1, 0, 0.05, 0.08, "Известный бизнесмен вложился и выкупил долговые обязательства банков-должников", '',
              '', '', 'Глобальная встревоженность понижена на', ""))
    CentralBank.EventsUnman.append(Event(1, 10000, 0.05, 0.08,
                                         "Десять тысяч рублей были востребованны правительством для поддержания бюджетной политики ",
                                         '', '', '', 'Глобальная встревоженность повышенна на', ""))
    CentralBank.EventsUnman.append(
        Event(1, 35000, 0.04, 0.09, "35000 рублей были выданны правительством для поддержания бюджетной политики", '',
              '', '', 'Глобальная встревоженность понижена на', ""))
    CentralBank.EventsUnman.append(Event(1, 22000, 0.13, 0.02,
                                         "Двадцать две тысячи рублей были востребованны правительством для поддержания бюджетной политики ",
                                         '', '', '', 'Глобальная встревоженность повышенна на', ""))
    CentralBank.EventsUnman.append(Event(1, 0, 0.1, 0.1,
                                         "",
                                         '', '', '', 'Глобальная встревоженность понижена на', ""))
    CentralBank.EventsUnman.append(
        Event(1, 3056, 0.14, 0.19, "Приобретение банком государственных ценных бумаг на сумму 3056 рублей", '', '', '',
              'Глобальная встревоженность понижена на', ""))
    CentralBank.EventsUnman.append(Event(1, 6455, 0.09, 0.17, "Покупка национальной валюты за 6455 рублей", '', '', '',
                                         'Глобальная встревоженность понижена на', ""))
    CentralBank.EventsUnman.append(Event(1, 0, 0.1, 0.1,
                                         "(что то связанное со ставкой процента)",
                                         '', '', '', 'Глобальная встревоженность понижена на', ""))
    CentralBank.EventsUnman.append(
        Event(1, 7000, 0.03, 0.06, "Выкуп отдельных облигаций федеральных займов на 7000 рублей", '', '', '',
              'Глобальная встревоженность понижена на', ""))
    CentralBank.EventsUnman.append(
        Event(1, 8000, 0.02, 0.13, "Погашение задолженности по средствам в иностранной валюте в размере 8000 рублей",
              '', '', '', 'Глобальная встревоженность понижена на', ""))
    CentralBank.EventsUnman.append(
        Event(1, 8046, 0.04, 0.01, "8046 рублей были выданны правительством для поддержания бюджетной политики", '', '',
              '', 'Глобальная встревоженность понижена на', ""))


def main():
    """main loop class"""
    initWorld()  # init
    for term in range(N_TERMS):
        CentralBank.inflation += randint(10, 20) / 100  # рост инфляции каждый "цикл"
        for q, bank in enumerate(CentralBank.banks):
            CentralBank.banks[q].term_sur += 1

            if q == PLAYER_BANK_N and PLAYER_ACTIVE:
                root = Tk()
                print("Статус на рынке:")
                print(CentralBank.statestatus())
                print("Установите Ставку резервирования (ROR) и Ставку процента по вкладам (ROD)")
                root.title(str("".join(("Параметры для срока  ", str(term), " / Принять".split("/")[0]))))
                ROR_scale = Scaling_window("".join(("Параметры для срока ", str(term), "/ROR Принять")),
                                           CentralBank.rate_on_reserves, 100)
                ROD_scale = Scaling_window("".join(("Параметры для срока ", str(term), " /ROD Принять")), 1, 100)
                root.geometry("550x100+300+300")
                root.mainloop()
                CentralBank.banks[q].rate_on_reserves = max(float(int(ROR_scale.var.get()) / 100),
                                                            CentralBank.rate_on_reserves)
                CentralBank.banks[q].rate_on_depo = max(float(int(ROD_scale.var.get()) / 100), 0.01)

                print("В периоде №", term, "  Игрок выбрал ставку резервирования и ставку по вкладам: ", CentralBank.banks[q].rate_on_reserves,
                      CentralBank.banks[q].rate_on_depo)
                if CentralBank.rate_on_reserves == CentralBank.banks[q].rate_on_reserves:
                    print("Процент резервирования по требованию  центробанка")
            is_bakcrupt, dropped_inv, dropped_depos = bank.dropDepos()
            if is_bakcrupt is True:  # если банк обанкротился
                if q == PLAYER_BANK_N:
                    for inv in bank.investors:
                        CentralBank.banks[q].gain -= inv.deposit
                    bank.bankrupt()
                    CentralBank.banks.pop(q)
                    print("Банк игрока обанкротился на сроке №", term, "После выплаты ", round(dropped_depos, 2),
                          "руб. депозитов", dropped_inv, "чел. ушедших вкладчиков")
                    return

            else:

                for i, inv in enumerate(bank.investors):
                    CentralBank.banks[q].reserve -= inv.deposit * bank.rate_on_depo  # выплачиваем проценты вкладчикам
                    CentralBank.banks[q].investors[i].deposit *= (bank.rate_on_depo + 1)
                    CentralBank.banks[q].investors[i].deposit /= (CentralBank.inflation + 1)
                CentralBank.banks[q].investments *= randint(5, 15) / 10
                s = CentralBank.banks[q].reserve + CentralBank.banks[q].investments  # все активы банка
                s /= (CentralBank.inflation + 1)
                CentralBank.banks[q].reserve, CentralBank.banks[q].investments = s * bank.rate_on_reserves, s * (
                        1 - bank.rate_on_reserves)
                # пересчитываем капитал банка (собрали все деньги и поделили по ставке)
                if PLAYER_BANK_N == q and PLAYER_ACTIVE:
                    print("Произошла выплата ", round(dropped_depos, 2),
                          "руб. депозитов", dropped_inv, "чел. ушедшим вкладчикам")
                    print("После выплаты процентов по вкладам и получения дохода от инвестиций у банка осталось",
                          round(s, 2), "руб. в активах",
                          f"из них {round(CentralBank.banks[q].investments, 2)} руб. в инвестициях, а {round(CentralBank.banks[q].reserve, 2)} руб. в резервах")
                if CentralBank.banks[q].investments < 0 or CentralBank.banks[q].reserve < 0:
                    for inv in bank.investors:
                        CentralBank.banks[q].gain -= inv.deposit
                    CentralBank.banks.pop(q)
                    bank.bankrupt()
                    if q == PLAYER_BANK_N:
                        print("Банк игрока обанкротился при выплате процента по вкладам")
                        return
            if EVENT_ACTIVE and q == PLAYER_BANK_N:
                shuffle(CentralBank.EventsMan)
                for event in CentralBank.EventsMan:
                    if randint(0, 100) < EVENT_CHANCE:
                        if event.param == 1:
                            event.playeventManagableCost(q)
                        else:
                            event.playeventManagableAwareness(q)
                        break
                shuffle(CentralBank.EventsUnman)
                for event in CentralBank.EventsUnman:
                    if randint(0, 100) < EVENT_CHANCE:
                        if event.param == 1:
                            event.playeventUnmanagableCost(q)
                        else:
                            event.playeventUnmanagableAwareness(q)
                        break
if __name__ == '__main__':
    replay = "Y"
    """Everybody wants to replay, aye!"""
    while (replay != ""):
        main()
        replay = input("Чтобы играть снова введите непустую строку")
