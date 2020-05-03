# Finite state Machine

We are trying to develop a piece of software which will act as a finite state machine. 

This is very nice concept - an object has a set number of possible states... And the object can **transitionion** from one **state** to **another** depending if some conditions are met.

## Lightbulb Finite State Machine

A lightbuild can either be 

  - On
  - Off
  
So it has two states.

It **transitions** from On -> Off when **Button is pressed down**, and similarly it transitions from Off -> On when **Button is released**.

### Example code


```text python
from statemachine import StateMachine, State
from graphviz import Digraph
from time import sleep


class LightBulb(StateMachine):
    """
    Simple Finite State Machine, to represent a lightbulb.
    """
    Off = State('Off', initial=True)
    On = State('On')
    turned_on = Off.to(On)
    turned_off = On.to(Off)


def plot_state_machine(state_machine, name='state_machine'):
    dg = Digraph(comment=name)
    for s in state_machine.states:
        for t in s.transitions:
            dg.edge(t.source.name, t.destinations[0].name)
    dg.render('./{}.gv'.format(name), format='png')


if __name__ == "__main__":
    kitchen_light = LightBulb()
    print(kitchen_light.current_state)
    print(f"turned_on  {kitchen_light.turned_on}")
    print(f"turned_off {kitchen_light.turned_off}")
    plot_state_machine(kitchen_light, 'Kitchen Light')
    # After 2 seconds something requires the light to be on
    sleep(2)
    kitchen_light.turned_on()
    print(kitchen_light.current_state)
    # After 2 seconds something requires the light to be off
    sleep(2)
    kitchen_light.turned_off()
    print(kitchen_light.current_state)
```

When this is run it should produce output like 

```text
State('Off', identifier='Off', value='Off', initial=True)
turned_on  CallableInstance(Transition(State('Off', identifier='Off', value='Off', initial=True), (State('On', identifier='On', value='On', initial=False),), identifier='turned_on'), func=<function Transition.__get__.<locals>.transition_callback at 0x102f1e550>, **{})
turned_off CallableInstance(Transition(State('On', identifier='On', value='On', initial=False), (State('Off', identifier='Off', value='Off', initial=True),), identifier='turned_off'), func=<function Transition.__get__.<locals>.transition_callback at 0x102f1e550>, **{})
State('On', identifier='On', value='On', initial=False)
State('Off', identifier='Off', value='Off', initial=True)
```

