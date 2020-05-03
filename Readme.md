# Finite state Machine

We are trying to develop a piece of software which will detect something like this

    @123#
    @1223443342#
    @1# 
    @@123# (pattern is @123#)
    
 Now I could write this as a RegEx ('@'(0-9)+'#') - but let us assume that this process is not solvable this way.
 
 Or we could try and think of this as a set of "states" - which are mapped out
 
 Something like this.
 
 ![./fsm_01.png](./fsm_01.png)
 
 #