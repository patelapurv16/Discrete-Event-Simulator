#Discrete - Event Simulator 
#Apurva Rajeshbhai Patel
#Section 0A06
#--------------------------------------------------------------------------------
#Importing the random, randint, sample from the random module
from random import random, randint, sample 
# Importing the matplotlib library as plt
import matplotlib.pyplot as plt
#The os module provides dozens of functions for interacting with the operating system
import os
# imports the path
import os.path

# Function to roll a weighted die.
#Returns True with probability p.
# else False.
def rolldie (p):
    '''Returns True with probability p.'''
    return(random() <= p)

# Our infection model is quite simple (see Carrat et al, 2008). People
# are exposed for E days (the incubation period), then infected for I
# additional days (the symptomatic period). Individuals are infectious
# as either E or I.  Carrat et al. (2008) indicate E~2 and I~7 for
# influenza.
#
# Recall status[] starts at E+I and counts down to REC=0.
#
# If I=7, E=2:
#   SUS REC                   I    E+I
#     |  |                    |     | 
#    -1  0  1  2  3  4  5  6  7  8  9
#          |===================||====|
# If I=7, E=2, Q =3 :
#   SUS REC         I-Q       I    E+I
#     |  |           |        |     | 
#    -1  0  1  2  3  4  5  6  7  8  9
#          |==========||======||==||====|

# Disease model. Each disease has a name, transmissivity coefficient,
# recovery coefficient, and exposure and infection times.  
class Disease():
    def __init__(self, name='influenza', t=0.95, E=2, I=7, r=0.0): 
        self.name = name
        self.t = t         # Transmissivity: how easy is it to pass on?
        self.E = E         # Length of exposure (in days)
        self.I = I         # Length of infection (in days)
        self.r = r         # Probability of lifelong immunity at recovery
        self.Q = 0         # Q is the number of days in a quarantine
        
#Compute the official String Representation of the object 
    def __repr__(self):
        '''Official String Representation of the object'''
        #Returns the representation
        return('<{}>'.format(self.name))

    # introduce a quarantine time to a disease
    # where Q cannot be longet than I
    #If it is than it will become equal to self.I,
    #Remains same otherwise
    def quarantine(self, Q):
        '''Quarantine for the Disease(Property of the Disease)'''
        # If Q greater than self.I
        if Q > self.I:
            #Sets equal to self.I
            self.Q = self.I
        #else remains the same 
        else:
            self.Q = Q

# Agent model. Each agent has a susceptibility value, a vaccination
# state, and a counter that is used to model their current E, I, R or
# S status.
class Agent():
    def __init__(self, group, cp):
        self.s = 0.99            # Susceptibility: how frail is my immune system?
        self.v = {}              # Vaccination state
        self.disease = {}        # Creating an empty dictionary so that I can keep track of the disease , that the agent has 
        self.q = 1.0             # probability of foolowing the quarantine which is set to 1.0(default)
        self.cp = cp             # list of contact probabilities
        self.group = group       # identifies the group of the agent
        self.Qtime= 0            # time in the quarantine
#Compute the Official String Representation of the object 
    def __repr__(self):
        '''Official String Representation of the object'''
        #returns the representation
        return('<{} v={} Q-time {}>'.format(self.disease, self.v, self.Qtime))

    # Method to impose a quarantine.
    #The quarantine is only imposed if the agent 
    # has the specified quarantined disease and  is in the I state, not already in a quarantine,
    # and is willing to be quarantined. 
    def illness(self, disease):
        '''Imposes quarantine when the agent is diseased and is willing to be quarantine'''
        # if the time in quarantine is 0 and rolldie is ttrue
        if self.Qtime== 0  and rolldie(self.q):
            #Imposes the quarantine by increasing it to 1
            self.Qtime= disease.Q + 1

    # Return True if infectious (i.e., in I or E state), False
    # otherwise.
    def state(self):
        '''Returns True if agent is infectious.'''
        # for every disease in the disease dictionary 
        for i in self.disease:
            # if the values of that dictionary is greater than 0
            if self.disease[i] > 0:
                #return True
                return(True)
        #Else return False 
        return(False)

    # Set the agent's vaccination value of that disease , to whatever value you give.
    def vaccinate(self, v, disease):
        '''Models vaccination; v=0 denotes full immunity; v=1 denotes no immunity.'''
        #Gives Vaccination for that particular Disease
        self.v[disease] = v
        
    # Susceptible: if other is infected, roll the dice and update your
    # state. No real need to check other.state() here, since it is
    # checked prior to invoking the method, but it is included as per
    # spec. Note also that I add 1 to I+E, because my first step in
    # run() is to update state: your code may differ. Finally, it's
    # important to "remember" which disease you have so that you can
    # handle recovery and susceptibility correctly when the disease
    # finally runs its course.
    def infect(self, other, disease):
        '''Other tries to infects self with disease.'''
        # Checks the agent is not in Quarantine and also checks that that person is infected , self is susceptible, rolldie to see whether the disease is infected 
        if other.Qtime == 0 and other.disease[disease] > 0 and self.disease[disease] == -1 and rolldie(self.s*self.v[disease]*disease.t*self.cp[other.group]):
            #Infects with the disease 
            self.disease[disease] = disease.I + disease.E + 1
            #return True if done
            return(True)
        #Else False 
        return(False)

    # Update the status of the agent. This involves decrementing your
    # internal counter if you are actively infected. When you get to
    # 0, you need to flip a (weighted) coin to decide if the agent
    # goes to state R (c=0) or back to state S (c=-1). Also, we need to
    # count down the quarantine if one is imposed. Finally, if an agent goes
    # into the Infected state, see if he will follow the quarantine (if one
    # been imposed)
    def update(self):
        '''Daily status update.'''
        # for the disease in disease dictionary
        for disease in self.disease:
            # if it is equal to 1 
            if self.disease[disease] == 1:
                # if it's False
                if not rolldie(disease.r):
                    # Revert to susceptible, c=-1.
                    self.disease[disease] = -1
                #Else
                else:
                    # recovery, c=0.
                    self.disease[disease] = 0
            #if the c is greater than 1
            if self.disease[disease] > 1:
                # One day closer to recovery.
                self.disease[disease] = self.disease[disease] - 1
            # if C is equal to I and Q is greater than 0
            if self.disease[disease] == disease.I and disease.Q > 0:
                    #Goes to illness and work accordingly 
                    self.illness(disease)
            #if the time in quarantine is greater than 0
            if self.Qtime> 0:
                    # Bring near to exit the quarantine
                    self.Qtime= self.Qtime- 1
   
    
            

# Simulation model. Each simulation runs for at most a certain
# duration, D, expressed in terms of days.
class Simulation():
    '''Simulation should run for the D Days'''
    def __init__(self, D=500, m=0.001, cpList= [[1.0]]):
        self.steps = D		    # Maximum Number of Days 
        self.agents = []            # List of agents in the simulation
        self.disease = []           # Disease being simulated
        self.history = {}           # History of (E, I, S, Q) tuples
        self.eventQ = []            # information of the quarantine (time, disease, Q)
        self.eventCamp = []         # information of the campaign (time, disease, coverage, v)
        self.history2 = []          # information of the seed
        self.cpList = cpList        # list of the cp
        self.m = m                  # mixing coefficient
        self.dName ={}              # Creating the dictionary ,containing the name of the disease ,
                                    #which will help calling the disease in the simulate as well as in the configuration method

    #Populates method Simulates with a certain number of agents in each group
    #having a list of contact probablities(cp), compliance probability q and
    #susceptibility(S)
    def populate(self, numGroup, group, cp):
        '''Populate simulation with n agents of each group, with specified q and s.'''
        #for i in the range of number of groups 
        for i in range(numGroup):
            # uses the join method to append the following information into the self.agent List 
            self.join(Agent(group=group, cp=self.cpList[group]))


    # Add agent to current simulation.
    def join(self, agent):
        '''Add specified agent to current simulation.'''
        #Appends the following agent to the self.agent list 
        self.agents.append(agent)
        
    # Compute the Official String Representation of the object
    def __repr__(self):
        '''Official String Representation of the Object'''
        #Returns the representation
        return("< simulation lasting {} days >".format(self.steps))

    # Fumction that removes the agent if there are no disease left in the 
    # Simulation 
    def getOut(self):
       '''Removes the agent if there are no disease left in the Simulation '''
       # setting a value of i equal to 0 
       i = 0
       # for every disease in my self.disease list
       for x in self.disease:
           # if that disease in my history dictionary is having the value of tuple (0,0)
           if self.history[x][-1][:2] == (0,0):
               # increment the value of i by 1
               i = i + 1
       # if the i is equal to the length of self.disease list 
       if i == len(self.disease):
           # return true  else
            return(True)
       #false otherwise
       return(False)

    # Adds multiple disease in the simulation
    # BY providing condition and vaccine state for each agentin the Simulation
    # moreover creates the value of the dictionary for disease() having an empty list of the history which will be filled further in codes
    def introduce(self, disease):
        '''Add specified disease to current simulation.'''
        # goes to the list of disease which was empty in the constructor
        self.disease.append(disease)
        # dictionary with disease name having the key == disease.name will have the value of the information of disease
        self.dName[disease.name] = disease
        #For the particular disease the value of that disease is equal to empty list which will be filled further in the codes 
        self.history[disease]=[]
        # for every agent in the self.agent List 
        for agent in self.agents:
            #Providing the condition
            agent.disease[disease] = -1
            #Providing the vaccination state
            agent.v[disease] = 1.0
            

    # Seed the simulation with k agents having the specified disease.
    def seed(self, disease, k=1):
        '''Seed a certain number of agents with a particular disease.'''
        # Add the disease to the simulation.
        # self.introduce(disease)
        # update() runs before the infect() method, I+E+1,
        #because my first step in run() is to update state
        #Also, remember what disease you have
        # for the agent in the sample(list, number of agent you want)
        for agent in sample(self.agents, k):
            #for the agent.disease dictionary of that disease --> infects by I+E+1
            agent.disease[disease] = disease.I + disease.E + 1

    # add a tuple with the particular information of campaign 
    def campaign(self, time, disease, coverage, v):
        # adds to the list of eventCamp
        self.eventCamp.append((time, disease, coverage, v))

    # add a tuple with the quarantine information 
    def quarantine(self, time, disease, Q):
        # adds to the list of eventQ
        self.eventQ.append((time, disease, Q))

    # add a tuple with seeding information 
    def seeding(self, time, disease, number):
        # adds the tuple to history2 List
        self.history2.append((time, disease, number))

    # This is where the simulation actually happens. The run() method
    # performs at most self.steps iterations, where each iteration
    # updates the agents, counts how many are in E and I states,
    # checks if there is an early termination (i.e., no contagious
    # agents left) and then is vaccination campaigns or quarantines have been
    # issued then they go into affect on the specified day. 
    def run(self):
        '''Run the simulation.'''
        i = 0
        while i < self.steps:
            # Update each agent, counting how many are still exposed
            # or infected.  Finding infected agents first avoids
            # letting the infection infect a friend's friend in one
            # pass.
            # Creating for the people who are contagious with some disease 
            contagious = [ a for a in self.agents if a.state() ]
            # creating for the people who are healthy with no disease 
            healthy = [ a for a in self.agents if not a.state() ]
            # for the contagious people updating there status 
            for a in contagious:
                # updated the status
                a.update()
            # if there is a quarantine run,
            # see if every agent will go into quarantine by calling the illness method
            # so , if the len of the history2 list is greater than 0
            if len(self.history2) > 0:
                # for j in the range of the len of the history2 list 
                for j in range(len(self.history2)):
                    # seed days == to value at the 0th place of  the history2[j]
                    sdDay = self.history2[j][0]
                    # seed disease == to the value at the 1st place of the history2[j]
                    sdDisease = self.history2[j][1]
                    # number of times goes to seed == to the value at the 2nd place of the history2[j]
                    sdNum = self.history2[j][2]
                    # if the value of i is equal to the number of days in the seed 
                    if i == sdDay:
                        #goes to the seed method having the parameter equal to disease in seed and num in seed
                        self.seed(sdDisease, sdNum)
            # if the length of the eventQ list is greater than 0
            if len(self.eventQ) > 0:
                # multiple quarantines can be issued
                #  run through the list of tuples in the self.eventQ
                # for j in the range of len of the self.eventQ List 
                for j in range(len(self.eventQ)):
                    # quarantine days is equal to the value at the 0th place of self.eventQ[j]
                    quarDay = self.eventQ[j][0]
                    # quarantine days is equal to the value at the 1st place of self.eventsQ[j]
                    quarDisease = self.eventQ[j][1]
                    # quarantine days is eqaul to the value at the 2nd place of self.eventsQ[j]
                    quarLen = self.eventQ[j][2]
                    # if today is the the quarantine event then rolldie on the contagious list
                    # to see if they follow a quarantine
                    if i == quarDay:
                        quarDisease.quarantine(quarLen)
            #if there is a campaign,
            #run the vaccine method for the list
            #of healthy agents with the probability  of coverage
            #Coverage here means  is the probability with which I vaccinate any given agent.
            #So if a vaccination campaign is in force with coverage=0.8 and vaccine effectiveness v=0.2,
            #I will consider each agent, flip a weighted coin that comes up True 80% of the time,
            #and if its True this time, I will set that agents internal v value to be 1-0.2=0.8
            # So if the len of the eventCamp list is greater than 0
            if len(self.eventCamp) > 0:
                # multiple campaigns can be issued 
                # run through the list of tuples in the self.eventCamp
                # for j in the range of the len of eventCamp List
                for j in range(len(self.eventCamp)):
                    # Campaign Day is equal to the value at the 0th place of the self.eventCamp[j]
                    campDay = self.eventCamp[j][0]
                    # Campaign Disease is equal to the value at the 1th place of the self.eventCamp[j]
                    campDisease = self.eventCamp[j][1]
                    # Campaign Coverage is equal to the value at the 2th place of the self.eventCamp[j]
                    campCoverage = self.eventCamp[j][2]
                    # Campaign Vaccine is equal to the value at the 3th place of the self.eventCamp[j]
                    campVaccine = self.eventCamp[j][3]
                    # if today is the campaign day then rolldie , so that
                    # I can know if a healthy agent will
                    # recieve the vaccine or not
                    # So if i is equal to CampDay
                    if i == campDay:
                        # for every agent in the healty which is mentioned above 
                        for agent in healthy:
                            # roll the die with the coverage of campaign as a parameter
                                if rolldie(campCoverage):
                                    # if rolldie is True vaccinate the agent with that particular disease 
                                    agent.vaccinate(campVaccine, campDisease)
            # Update the history with exposed and infected counts.
            # create a dict for each disease and add the number of E, I, Susceptible, and Quarantined
            # note that S is represented by the sum of the vaccine values in the healthy list
            # for every disease in the self.disease dictionary
            for disease in self.disease:
                # for that disease key -- value ( append to the value to that list with the particula information)which contains the tuple of
                # number of infected days , exposed days , vaccination for that disease , condition.
                self.history[disease].append((len([ a for a in contagious if a.disease[disease] > disease.I ]),
                                              len([ a for a in contagious if a.disease[disease] <= disease.I ]),
                                              sum([ a.v[disease] for a in self.agents]),
                                              len([ a for a in contagious if a.Qtime > 0 and a.disease[disease] <= disease.I])))
            #Exit early if there are no infected agents left.
            # if the guy terminate and the value of i is greater than maximum value of time step
            if self.getOut() and i > max([x[0] for x in self.history2]):
                #return my history list having the tuple(I,E,S,Q)
                return(self.history)
            # if it terminate early it won't get into the next step but if it doesn't then the following things.
            # for agent in the contagious 
            for a1 in contagious:
                # Let's see who a1 can infect. No need to check
                # a2.state() here, as a2.infect() will check it for
                # you. Note the use of the mixing parameter to
                # determine if a1 and a2 have been in contact with
                # each other today. Also, allow all diseases a chance to
                # infect self
                # only change in project 2 is to allow an agent to infect their neighbor with all disease
                # they have (run through the dict of diseases)
                # for agent is self.agents 
                for a2 in self.agents:
                    # checks if the agents came into contact
                    if rolldie(self.m):
                        #if True , means aget came in contact
                        # for disease in self.disease 
                        for k in self.disease:
                            #agent k infects agent a1
                            a2.infect(a1, k)
            #incrementing the value of i by 1
            i = i + 1
        # Return the history of (E, I,S,Q) tuples.
        #return([self.history[disease] for disease in self.history])

    # Plots the Graph
    def plot(self, disease):
        '''Produce a pandemic curve for the simulation.'''
        #Title of the plot
        plt.title(disease.name)
        #x - axis label
        plt.xlabel('Days')
        #y - axis label 
        plt.ylabel('N')
        # plotting for the expose
        plt.plot( [ i for i in range(len(self.history[disease])) ], [ e for (e, i, s, q) in self.history[disease] ], 'g-', label='Exposed' )
        # plotting for infected
        plt.plot( [ i for i in range(len(self.history[disease])) ], [ i for (e, i, s, q) in self.history[disease] ], 'r-', label='Infected' )
        # plotting for susceptible
        plt.plot( [ i for i in range(len(self.history[disease])) ], [ s for (e, i, s, q) in self.history[disease] ], 'b-', label='Susceptible' )
        # plotting for quarantine
        plt.plot( [ i for i in range(len(self.history[disease])) ], [ q for (e, i, s, q) in self.history[disease] ], 'y-', label='Quarantine' )
        # plt.legend will make a block of information at upper right conner of the graph providing information about the plotting pandamic curve
        plt.legend(['Exposed','Infected','Susceptible','Quarantine'],loc = 'upper right')
        # show the graph
        plt.show()
    #Config method opens the file and reads the file in the simulation (like the Simulate top level Function)
    def config(self,filename):
        '''Takes the input from the file and run accordingly'''
        if not os.path.isfile(filename) and not os.access(filename, os.R_OK):
            print ("Either {} is missing or is not readable".format(filename))
        else:          
            # opens the file and read it ('r' indicates reading)
            file=open(filename, 'r')
            # for every line in file
            for lines in file:
                # lowering the lines and splitting it which will give a list of splitted input commands
                A = lines.lower().split()
                # if the  first word of the line  is equal to add
                if A[0] =='add':
                    # call the populate function
                    self.populate(eval(A[1]), eval(A[2]), self.cpList[eval(A[2])])
                    # String representation
                    print("{} agents of group {} having cp of {}".format(A[1],A[2],self.cpList[eval(A[2])]))
                # if its equal to disease 
                elif A[0] == 'disease':
                    # call the introduce function
                    self.introduce(Disease(name=eval("A[1]"), t=eval(A[2]), E=eval(A[3]), I=eval(A[4]), r=eval(A[5])))
                    # String representation 
                    print("introduce {} with transitivity {},  {} exposed days, {} infected days and having recovery {}".format(A[1],A[2],A[3],A[4],A[5]))                    
                # if its equal to the seed
                elif A[0] == 'seed':
                    #calls the seed method
                    self.seeding(eval(A[1]), self.dName[eval("A[2]")], eval(A[3]))
                    # String representation
                    print("Day {} : seeding {} agents with {}".format(A[1],A[3],self.dName[eval("A[2]")]))
                # if its equal to the quarantine
                elif A[0] == 'quarantine':
                    #calls the quarantitne method
                    self.quarantine(eval(A[1]), self.dName[eval("A[2]")], eval(A[3]))
                    #String representation
                    print("{}: Establishing {} agents with {}".format(A[1],A[3],self.dName[eval("A[2]")]))
                # if its equal to campaign
                elif A[0] == 'campaign':
                    #calls the campaign method
                    self.campaign(eval(A[1]), self.dName[eval("A[2]")], eval(A[3]), eval(A[4]))
                    #String Representation 
                    print("Day {} : {}  of uninfected agents by {} will be vaccinated with effectiveness {}".format(A[1],A[3] , self.dName[eval("A[2]")], A[4])) 
                    # if its equal to run
                elif A[0] == 'run':
                    # runs the code
                    self.run()
                    #String representation
                    print("{} the Simulation ".format(A[0]))
                # print(a.history)(for debugging the codes)
                # if its equal to plot
                elif A[0] == 'plot':
                    # plots the graph
                    self.plot(self.dName[eval("A[1]")])
                    #String representation
                    print("plot graph for {}".format(self.dName[eval("A[1]")]))
                else:
                    # prints an error if the commands provided by the user is not correct 
                    print("Error , Please! enter a valid commands in the File")
        


# Creating a test Function to check the codes at a certain point 
def test():
    '''Test the codes'''
    # Creating the Simulation object
    S=Simulation(D=1000)
    # setting the value of mixing probability
    S.m = 0.001
    # creating a contact probability List
    S.cpList = [[.5,0,0],[0,.5,0],[0,1,1]]
    # Calling the populate for every agent type with its cp
    S.populate(100, 0, S.cpList[0])
    S.populate(100, 1, S.cpList[1])
    S.populate(100, 2, S.cpList[2])
    # creating the disease object
    x=Disease(name = "influenza",t=.95, E=2, I = 7, r=.2)
    #creating another disease object
    y=Disease(name = "mumps")
    # calling the introduce method on x object of the disease
    S.introduce(x)
    #calling the introduce method on y object of the disease
    S.introduce(y)
    #calling the seeding method x
    S.seeding(10,x, 1)
    #calling the seeding method for y
    S.seeding(40,y,1)
    #Calling the campaign method
    S.campaign(20, x, .9, .1)
    #Calling the quarantine method 
    S.quarantine(0, y, 5)
    #calling my seed method on x
    S.seed(x,1)
    #calling my seed method on y 
    S.seed(y,1)
    #runs the codes 
    S.run()
    #plot for x 
    S.plot(x)
    # Plot for y 
    S.plot(y)
    #returns Simulation object
    return(S)

def Simulate():
    '''Takes input from user and implement the codes  accordingly'''
    #setting a variable equal to True 
    B = True
    #This step will iterate till the user inputs "Bye"
    #Thus creating a While loop
    while B == True:
        # Creating the input command 
        C = input('Sim> ')
        # if the user doesn't provide an command in the input 
        if C == '' :
            # it will print the following message 
            print("Please, try again by putting a valid command , Thank you :)".format())
        #Else it will work according to the commands provided by the user
        else:
            # Splitting whatever the user puts the input and converting all the string values in the lower case
            #so that even if the user says "QUARANTINE" i can implement it as quarantine
            A = C.lower().split()
            # if the first element in the list is new 
            if A[0] == 'new':
                # Creating an object for simulation
                S=Simulation(eval(A[1]))
                # mixing probability
                S.m = eval(A[2])
                # contact probability 
                S.cpList = eval(A[3])
                # prints the format with the new days assigned 
                print('Simulation with {} days, {} mixing probability, {} contact probability(cp) list'.format(A[1],A[2],A[3]))
            # if the firt element is add
            elif A[0] =='add':
                # calling the populate method of the simulation 
                S.populate(eval(A[1]), eval(A[2]), S.cpList[eval(A[2])])
                print("Simulation with {} agents of group {} having contact probability  at position {} of cpList".format(A[1],A[2],A[2]))
            # if the first element is disease
            elif A[0] == 'disease':
                # calling the introduce method of the Simulation
                S.introduce(Disease(name=A[1], t=eval(A[2]), E=eval(A[3]), I=eval(A[4]), r=eval(A[5])))
                # String representation 
                print("introduce {} with transitivity {}, {} exposed days,  {} infected days and having recovery {}".format(A[1],A[2],A[3],A[4],A[5]))  
            # if the first element is seed
            elif A[0] == 'seed':
                #a = self.dName[eval("A[2]")]
                #calling my seeding method
                S.seeding(eval(A[1]), S.dName[A[2]], eval(A[3]))
                # String representation
                print("Day {} : seeding {} agents with {}".format(A[1],A[3],A[2]))
            # if the first element is quarantine
            elif A[0] == 'quarantine':
                #calling the quarantine method of the simulation 
                S.quarantine(eval(A[1]),S.dName[A[2]], eval(A[3]))
                #String representation
                print("{}: Establishing {} agents with {}".format(A[1],A[3],A[2]))
            # if the first element is campaign
            elif A[0] == 'campaign':
                #calling the campaign method of the simulation                
                S.campaign(eval(A[1]), S.dName[A[2]], eval(A[3]), eval(A[4]))
                #String Representation 
                print("Day {} : {}  of uninfected agents by {} will be vaccinated with effectiveness {}".format(A[1],A[3] , A[2], A[4]))
            # if the first element is run 
            elif A[0] == 'run':
                #runs the simuation 
                S.run()
                #String representation
                print("{} the Simulation ".format(A[0]))
                #print(a.history)( for debugging my codes)
            # if the first element is plot
            elif A[0] == 'plot':
                # plot the graph
                S.plot(S.dName[A[1]])
                #String representation
                print("plot graph for {}".format(A[1]))
            # if the first element is bye 
            elif A[0] == 'bye':
                #String representation
                print('Good{}! See you again . Have a great Day!, My Friend!'.format(A[0]))
                # return the history of the simulation
                return(S.history)              
                
                # set the value of B = False when the user says bye so that it stops iterating
                B = False
            # else ,if the user doesnt input a valid command 
            else:
                # print this statement 
                print("Oh! No! ,It's an error, My Friend!"
                      "Please! print a valid command".format())


        
    


