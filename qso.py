import logging
import re

import daiquiri
from graphviz import Digraph
from statemachine import StateMachine, State

"""
Finite state Machine for FT8 QSO

This is rather basic at the moment, mainly as I have not coded a FSM before.

Whilst this does work the "plumbing" specifically the FSM_Matches is painful, I would like to 
be able to explore how to add this functionality in the definition of 

            t1_hear_a_cq = listen_1.to(hear_cq_2,Regex=r'XXyyzz')
"""


class FakeFt8Listener:
    """
    Base class so I can have some more tests cases
    """
    def __init__(self):
        self.logger = daiquiri.getLogger(__name__)
        self.pos = 0
        self.qso = []

    def listen(self):
        try:
            old_pos = self.pos
            self.pos += 1
            msg = self.qso[old_pos].split("~")[1].strip().upper()
            self.logger.debug(f"Msg is <{msg}>")
            return msg
        except:
            raise ValueError("No more data")


class FakeFT8Listener_good(FakeFt8Listener):
    """
    FT8 Basic QSO.
    Please ignore the fields before the tilde (~) - I am only using the MSG content.
    """
    def __init__(self):
        super().__init__()
        self.qso = """012545   5  0.2 1608 ~ CQ BI4VNM PM01            
012604  Tx      1555 ~  BI4VNM DU3TW PK05         
012815   2  0.0 1610 ~  DU3TW Bi4VNM +00         
012815   2  0.0 1610 ~  Bi4VNM DU3TW -05         
012815   2  0.0 1610 ~  DU3TW Bi4VNM  RRR         
012815   2  0.0 1610 ~  Bi4VNM DU3TW  RR73         
""".split(
            "\n"
        )


class FakeFT8Listener_little_noise(FakeFt8Listener):
    """
    FT8 Basic QSO.
    Please ignore the fields before the tilde (~) - I am only using the MSG content.
    """
    def __init__(self):
        super().__init__()
        self.qso = """012545   5  0.2 1608 ~ CQ BI4VNM PM01            
012604  Tx      1555 ~  BI 4V DTW PK05         
012604  Tx      1555 ~  BI4VNM DU3TW PK05         
012815   2  0.0 1610 ~  DU3TW Bi4VNM +00         
012815   2  0.0 1610 ~  Bi4VM DUW 5
012815   2  0.0 1610 ~  Bi4VNM DU3TW -05         
012815   2  0.0 1610 ~  DU3TW Bi4VNM  RRR         
012815   2  0.0 1610 ~  Bi4VNM DU3TW  RR73         
""".split(
            "\n"
        )


class QsoMachine(StateMachine):
    """
    These are the states
    """

    """
    This is Pounce mode FT8
                                                        States 
                                                        Listen
                                                        Listen
    012545   5  0.2 1608 ~  CQ BI4VNM PM01     China    hear_cq            
    012604  Tx      1555 ~  BI4VNM DU3TW PK05           reply_to_cq
    012815   2  0.0 1610 ~  DU3TW Bi4VNM +00            get_rst
    012815   2  0.0 1610 ~  Bi4VNM DU3TW -05            send_rst
    012815   2  0.0 1610 ~  DU3TW Bi4VNM  RRR           get_bye
    012815   2  0.0 1610 ~  Bi4VNM DU3TW  RR73          send_bye
    """
    listen_1 = State("listen_for_activity", initial=True)
    hear_cq_2 = State("hear_cq")
    reply_to_cq_3 = State("reply_to_cq")
    get_rst_4 = State("get_rst")
    send_rst_5 = State("send_rst")
    get_bye_6 = State("get_bye")
    send_bye_7 = State("send_bye")
    finished_8 = State("finished")

    """
    These are the transitions - Simplified
    """
    t1_hear_a_cq = listen_1.to(hear_cq_2)
    t2_reply_to_a_cq = hear_cq_2.to(reply_to_cq_3)
    t3_get_rst = reply_to_cq_3.to(get_rst_4)
    t4_send_rst = get_rst_4.to(send_rst_5)
    t5_get_bye = send_rst_5.to(get_bye_6)
    t6_send_bye = get_bye_6.to(send_bye_7)
    t7_end_qso = send_bye_7.to(finished_8)

    FSM_Matches = (
        # RegEx, curState, transaction_to_trigger
        {"regex": r"^[C][Q][ ]", "cur_state": listen_1, "transaction": t1_hear_a_cq},
        {
            "regex": r"([A-Z0-9]{4,})[ ]+([A-Z0-9]{4,})[ ]+([A-Z0-9]{4,6})",
            "cur_state": hear_cq_2,
            "transaction": t2_reply_to_a_cq,
        },
        {
            "regex": r"([A-Z0-9]{4,})[ ]+([A-Z0-9]){4,}[ ]+([0-9+\-]{2,3})",
            "cur_state": reply_to_cq_3,
            "transaction": t3_get_rst,
        },
        {
            "regex": r"([A-Z0-9]{4,})[ ]+([A-Z0-9]){4,}[ ]+([0-9+\-]{2,3})",
            "cur_state": get_rst_4,
            "transaction": t4_send_rst,
        },
        {
            "regex": r"([A-Z0-9]{4,})[ ]+([A-Z0-9]){4,}[ ]+([A-Z0-9]{3,})",
            "cur_state": send_rst_5,
            "transaction": t5_get_bye,
        },
        {
            "regex": r"([A-Z0-9]{4,})[ ]+([A-Z0-9]){4,}[ ]+([A-Z0-9]{4,})",
            "cur_state": get_bye_6,
            "transaction": t6_send_bye,
        },
        {
            "regex": r"([A-Z0-9]{4,})[ ]+([A-Z0-9]){4,}[ ]+([A-Z0-9]{4,})",
            "cur_state": send_bye_7,
            "transaction": t7_end_qso,
        },
    )

    def __init__(self):
        self.logger = daiquiri.getLogger(__name__)
        super().__init__()
        self.MAX_FAILS = 3

    # def on_hear_a_cq(self):
    #     print('Heard a Cq')
    #
    # def on_reply_to_a_cq(self):
    #     print('reply to a q')

    def plot_state_machine(self):
        name = __name__
        dg = Digraph(comment=name)
        for s in self.states:
            for t in s.transitions:
                dg.edge(t.source.name, t.destinations[0].name)
        dg.render("./{}.gv".format(name), format="png")

class FSMQso:
    def __init__(self, listener):
        self.logger = daiquiri.getLogger(__name__)
        self.FSM = QsoMachine()
        self.qso = listener

    def read(self) -> str:
        line_data = self.qso.listen()
        self.logger.debug(f"Current State is {self.FSM}")
        return line_data


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logger = daiquiri.getLogger(__name__)
    good_qso = FakeFT8Listener_good()
    smqso = FSMQso(good_qso)
    transaction_fail_count = 0
    smqso.FSM.plot_state_machine()
    logger.info("State Machine output as png")
    try:
        while True:
            data = smqso.read()
            # print(smqso.FSM.current_state)
            logger.debug(f"State -> {smqso.FSM.current_state_value}")

            for i in smqso.FSM.FSM_Matches:
                if i["cur_state"] == smqso.FSM.current_state:

                    if re.match(i["regex"], data):
                        """
                        Want to invoke the Transaction as the rule matches, and we are in the correct state
                        """
                        logger.info(f"Regex {i['regex']} matched match {data}")
                        wanted_transaction = i["transaction"]
                        smqso.FSM.run(wanted_transaction.identifier)
                        transaction_fail_count = 0
                        break
                    else:
                        logger.debug(f"Regex {i['regex']} does not match {data}")
                        break
                transaction_fail_count += 1
            if transaction_fail_count > smqso.FSM.MAX_FAILS:
                print("Max Fails Exceeded")
    except ValueError:
        print("Data finished")
    logger.debug(f"State -> {smqso.FSM.current_state_value}")