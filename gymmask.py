import numpy as np

# x = 0 # Base payoff
# m = 0 # Mask cost
# p = 0 # Mask protection benefit (function of n)
# s = 0 # Social protection benefit (function of n and b)
# n = 0 # Number of connected nodes cooperating
# nt = 0 # Total number of people in the gym
# b = 0 # Percieved social pressure belief 
# c = 0 # Percieved Covid cost (multiple distrubution, function of defectors (nt - n))

class gym_class:
    def __init__(self):
        self.covid_amount = 0
        self.area = 0 # create as area dimensions later
        self.number_of_agents = 0
        self.agents = [] # array of agents in gym
        self.num_cooperators = 0
        self.num_defectors = 0
    
    def add_coopr_agent(self):
        this_agent = agent()
        this_agent.action = 1
        this_agent.enter(self)

    def add_defct_agent(self):
        this_agent = agent()
        this_agent.action = 0
        this_agent.enter(self)

    def pop_agent(self):
        did_exit = False
        for i in self.agents:
            if i.present == True:
                i.exit(self)
                did_exit = True
                break
        if (not did_exit):
            print("No one is present in the gym")

    def remove_agent(self, index):
        self.agents[index].exit(self)

    def print_agent_list(self):
        print("[", end='')
        for i_count, i in enumerate(self.agents):
            if(i.present):
                print(i.index, end='')
            else:
                print(" ", end='')
            if(i_count == len(self.agents)-1):
                print("]")
            else:
                print(", ", end='')

    def num_agents(self):
        print(self.number_of_agents)

class agent:
    def __init__(self):
        ## A: Agent variables
        self.action = 'C' 
        self.present = False
        self.index = 0   
        self.total_payoff = 0

        ## B: Network edge parameters
        self.neighbors = []
        self.perceived_coopr = 0
        self.perceived_defect = 0

        ## C: Payoff constants
        self.base_payoff = 0 
        self.mask_cost = 2 

        ## D: Belief multipliers:
        self.protection_mult = 5
        self.social_pressure_mult = 0

        ## E: Covid parameters
        self.transmission_prob = 0.1
        self.self_cost = 2
        self.others_cost = 5
        assert (self.transmission_prob >= 0 and self.transmission_prob <= 1)
        
    def assess_neighbor_count(self):
        for i in self.neighbors:
            if (i.action == 'C'):
                self.perceived_coopr += 1
            elif (i.action == 'D'):
                self.perceived_defect += 1
            else:
                pass

    def protection_benefit(self, num_defectors): #p(b)
        return self.protection_mult * num_defectors    

    def social_pressure(self, num_cooperators): #s(n,b)
        return self.social_pressure_mult * num_cooperators

    def covid_cost(self, num_defectors): #c(nt -n)
        return self.transmission_prob * (self.self_cost + self.others_cost) * num_defectors
    
    def cooperate_payoff(self, gym):
        self.total_payoff = self.base_payoff 
        + self.protection_benefit(gym.num_defectors) + self.social_pressure(gym.num_cooperators)
        - self.mask_cost - self.covid_cost(gym.num_defectors)

    def enter(self, gym):
        gym.number_of_agents = gym.number_of_agents+1 
        if(self.action == 1):
            gym.num_cooperators += 1
        else:
            gym.num_defectors += 1

        self.present = True
        gym.agents.append(self)

        self.index = len(gym.agents)-1 # non-shrinking data structure
        for i in gym.agents:
            if (i.present):
                self.interact(i, gym)

    def exit(self, gym):
        if (self.present):
            gym.number_of_agents = gym.number_of_agents - 1
            if(self.action == 1):
                gym.num_cooperators -= 1
            else:
                gym.num_defectors -= 1
            self.present = False
        else:
            print("agent index", self.index ,"not present")

    def interact(self, other, gym):
        x = self.base_payoff
        m = self.mask_cost
        nt = gym.num_cooperators
        n = 0 # changed

        b = self.social_benefit
        s = self.social_pressure
        c = self.covid_cost

        # CC 
        if(self.action == 1 and other.action == 1):
            # x - m + p + s*n
            self.total_payoff = self.base_payoff + self.mask_cost 
            + self.social_benefit + self.social_pressure*gym.num_cooperators

        # CD
        elif(self.action == 1 and other.action == 0):
            self.total_payoff = self.base_payoff + self.mask_cost 
            + + self.social_benefit + self.social_pressure*gym.num_cooperators-1
        # DC
        elif(self.action == 0 and other.action == 1):
            pass
        # DD
        else:
            pass

    

def test_interact():
    gym = gym_class()
    gym.add_coopr_agent()
    gym.add_coopr_agent()

def test_basics():
    print("nice")
    #matrix = np.zeros((2,2), dtype='i,i')
    gym = gym_class()
    gym.add_coopr_agent()
    gym.add_coopr_agent()
    gym.add_coopr_agent()
    gym.print_agent_list()
    assert(gym.number_of_agents == 3)
    for i_count,i in enumerate(gym.agents):
        assert(i.index == i_count)

    kill_listA = [0,2]
    for i in kill_listA:
        gym.remove_agent(i)

    gym.print_agent_list()
    assert(gym.number_of_agents == 1)
    for i in kill_listA:
        assert(gym.agents[0])

    gym.remove_agent(2)

    gym.add_coopr_agent()
    gym.add_coopr_agent()
    gym.print_agent_list()

    gym.pop_agent()
    gym.pop_agent()
    gym.print_agent_list()
    gym.num_agents()


def main():
    test_basics()
    #test_interact()

if __name__ == '__main__':
    main()