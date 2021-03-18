from threading import Thread, Lock, Condition
from collections import deque
from random import randint as rnd
from time import sleep, time

'''
1st version of concypto.

1. Users and validators are generated randomly in given intervals.
2. All transactions of valid amount made by valid sender and sent to valid recievers are considered valid.
3. Information on amount of money in the system or money in posession of users and validators is not taken care of.
4. Transactions waiting to be validated and validated ones are stored in simple global containers simulating peer-to-peer connection.
5. No blockchain is involved, transactions are simply stored in deque structures.

...

Waiting transaction are in form:
(sender_id, receiver_id, amount, time_of_making_transaction)

Validated transaction are in form:
(sender_id, receiver_id, amount, time_of_making_transaction, validator_id, time_of_validating_transaction)

'''

#constants
fnou = 10 # final number of users
fnov = 5 # final number of validators

minuj, maxuj = 1, 5 #  span of seconds before new user joins the system
minuw, maxuw = 1, 5 # span of seconds user waits to make transaction

minvj, maxvj = 1, 5 #  span of seconds before new validator joins the system
minvw, maxvw = 1, 5 # span of seconds validator waits (needs) to validate transaction

minta, maxta = 1, 1000 # span of transaction amount

mclk = 10 # monitoring clock - every mclk seconds transactions will be printed out

#global vars
waiting_trans = deque()
valid_trans = deque()
num_of_users = 0
num_of_validators = 0

#concurrent primitives 
lock = Lock()
cv = Condition()

def trans_valid(trans):
    global num_of_users
    sender_valid =  trans[0] >= 0 and trans[0] < num_of_users
    reciever_valid =  trans[1] >= 0 and trans[1] < num_of_users
    amount_valid = trans[2] >= minta and trans[2] <= maxta 
    return sender_valid and reciever_valid and amount_valid

def generate_trans(user):
    return (user, rnd(0, num_of_users - 1), rnd(minta, maxta), time())

def user_trans_generator(user):
    global num_of_users
    while(True):
        if num_of_users > 2:
            cv.acquire()
            trans = generate_trans(user)
            with lock:
                waiting_trans.append(trans)
            cv.notify()
            cv.release()
            sleep(rnd(minuw, maxuw))

def generate_valid_trans(trans, validator):
    return ((trans + (validator, time())))

def validate_trans_generator(validator):
    while(True):
        cv.acquire()
        while not waiting_trans:
            cv.wait()
        with lock:
            trans = waiting_trans.popleft()
        cv.release()
        if trans_valid(trans):
            validated_trans = generate_valid_trans(trans, validator)
            valid_trans.append(validated_trans)
        sleep(rnd(minvw, maxvw))

def user_generator():
    global num_of_users
    user_threads = []
    for user in range(fnou):
        t = Thread(target = user_trans_generator, args = [user])
        t.start()
        user_threads.append(t)
        num_of_users += 1
        with lock:
            print('New user joined the system! His id: u' +  str(user))
        sleep(rnd(minuj, maxuj))

def validator_generator():
    global num_of_validators
    validator_threads = []
    for validator in range(fnov):
        t = Thread(target = validate_trans_generator, args = [validator])
        t.start()
        validator_threads.append(t)
        num_of_validators += 1
        with lock:
            print('New validator joined the system! His id: v' + str(validator))
        sleep(rnd(minvj, maxvj))


#generating users and validators
user_gen_thread = Thread(target = user_generator)
validator_gen_thread = Thread(target = validator_generator)
user_gen_thread.start()
validator_gen_thread.start()

#monitoring system on terminal
while(True):
    sleep(mclk)
    with lock:
        print('---------------\nWaiting transactions:\n---------------')
        for i in waiting_trans:
            print(i)
        print('---------------\nValidated transactions:\n---------------')
        for i in valid_trans:
            print(i)
        print('---------------')
    

        